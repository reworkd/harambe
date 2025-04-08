import asyncio
import inspect
import tempfile
import uuid
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Protocol,
    Union,
    Unpack,
    cast,
    Tuple,
)

import aiohttp
from bs4 import BeautifulSoup, Doctype
from playwright.async_api import (
    ElementHandle,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)

from harambe.cache import single_value_cache
from harambe.contrib import WebHarness, playwright_harness
from harambe.contrib.soup.impl import SoupPage
from harambe.contrib.types import AbstractPage
from harambe.cookie_utils import fix_cookie
from harambe.handlers import (
    ResourceRequestHandler,
    ResourceType,
)
from harambe.html_converter import HTMLConverterType, get_html_converter
from harambe.pagination import DuplicateHandler
from harambe.tracker import FileDataTracker
from harambe.types import (
    URL,
    AsyncScraperType,
    Context,
    HarnessOptions,
    Options,
    ScrapeResult,
    SetupType,
    Stage,
    Cookie,
    LocalStorage,
)
from harambe_core import SchemaParser, Schema
from harambe_core.errors import default_error_callback
from harambe_core.normalize_url import normalize_url
from harambe_core.observer import (
    ObservationTrigger,
    DownloadMeta,
    HTMLMetadata,
    OutputObserver,
    LoggingObserver,
    LocalStorageObserver,
)
from harambe_core.parser.expression import ExpressionEvaluator


class AsyncScraper(Protocol):
    """
    Protocol that all class based scrapers should implement.
    Note that scrapers in harambe should be functions, not classes.
    """

    async def scrape(self, sdk: "SDK", url: URL, context: Context) -> None: ...


class SDK:
    """
    As part of code generation, Reworkd generates code in its own custom SDK called [Harambe](https://github.com/reworkd/harambe).
    Harambe is web scraping SDK with a number of useful methods and features for:
    - Saving data and validating that the data follows a specific schema
    - Enqueuing (and automatically formatting) urls
    - De-duplicating saved data, urls, etc
    - Effectively handling classic web scraping problems like pagination, pdfs, downloads, etc

    These methods, what they do, how they work, and some examples of how to use them will be highlighted below.
    """

    def __init__(
        self,
        page: AbstractPage[Any],
        run_id: Optional[str] = None,
        domain: Optional[str] = None,
        stage: Optional[Stage] = None,
        observer: Optional[Union[OutputObserver, List[OutputObserver]]] = None,
        scraper: Optional[AsyncScraperType] = None,
        context: Optional[Context] = None,
        schema: Optional[Schema] = None,
        deduper: Optional[DuplicateHandler] = None,
        evaluator: Optional[ExpressionEvaluator] = None,
    ):
        self.page: Page = page  # type: ignore
        self._id = run_id or uuid.uuid4()
        self._domain = domain
        self._stage = stage
        self._scraper = scraper
        self._context = context or {}
        self._validator = SchemaParser(schema, evaluator) if schema else None
        self._saved_data: set[ScrapeResult] = set()
        self._saved_cookies: List[Cookie] = []
        self._saved_local_storage: List[LocalStorage] = []

        if not observer:
            observer = [LoggingObserver()]

        if not isinstance(observer, list):
            observer = [observer]

        self._observers = observer
        self._deduper = DuplicateHandler()
        self._deduper = deduper if deduper else DuplicateHandler()

    async def save_data(self, *data: ScrapeResult) -> None:
        """
        Save scraped data and validate its type matches the current schema

        :param data: Rows of data (as dictionaries) to save
        :raises SchemaValidationError: If any of the saved data does not match the provided schema
        :example:
            >>> await sdk.save_data({ "title": "example", "description": "another_example" })
        """
        if len(data) == 1 and isinstance(data[0], list):
            raise TypeError(
                "`SDK.save_data` should be called with one dict at a time, not a list of dicts."
            )

        source_url = self.page.url
        for d in data:
            if self._validator is not None:
                d = self._validator.validate(d, base_url=source_url)
            d["__url"] = source_url
            await self._notify_observers("on_save_data", d)

    async def enqueue(
        self,
        *urls: URL | Awaitable[URL],
        context: Optional[Context] = None,
        options: Optional[Options] = None,
    ) -> None:
        """
        Enqueue url(s) to be scraped later.

        :param urls: urls to enqueue
        :param context: additional context to pass to the next run of the next stage/url. Typically just data that is only available on the current page but required in the schema. Only use this when some data is available on this page, but not on the page that is enqueued.
        :param options: job level options to pass to the next stage/url

        :example:
            >>> await sdk.enqueue("https://www.test.com")
            >>> await sdk.enqueue("/some-path") # This will automatically be converted into an absolute url
        """
        context = context or {}
        options = options or {}
        context["__url"] = self.page.url
        base_url = await self._compute_base_url(self.page.url)

        for url in urls:
            if inspect.isawaitable(url):
                url = await url

            normalized_url = normalize_url(url, base_url) if base_url else url
            await self._notify_observers(
                "on_queue_url", normalized_url, context, options
            )

    @single_value_cache("__base_url_cache")
    async def _compute_base_url(self, current_url: str) -> URL:
        maybe_base_url = await self.page.query_selector("base")
        if not maybe_base_url:
            return current_url

        base_url = await maybe_base_url.get_attribute("href")
        if not base_url:
            return current_url

        return normalize_url(base_url, current_url)

    async def paginate(
        self,
        get_next_page_element: Callable[..., Awaitable[URL | ElementHandle | None]],
        timeout: int = 2000,
    ) -> None:
        """
        SDK method to automatically facilitate paginating a list of elements.
        Simply define a function that should return any of:
            - A direct link to the next page
            - An element with hrefs to the next page
            - An element to click on to get to the next page

        And call `sdk.paginate` at the end of your scrape function. The element will automatically be used to paginate the site and run the scraping code against all pages
        Pagination will conclude once all pages are reached no next page element is found.

        This method should ALWAYS be used for pagination instead of manual for loops and if statements.

        :param get_next_page_element: the url or ElementHandle of the next page
        :param timeout: milliseconds to sleep for before continuing. Only use if there is no other wait option

        :example:
            >>> async def pager():
            >>>     return await page.query_selector("div.pagination > .pager.next")
            >>>
            >>> await sdk.paginate(pager)
        """
        try:
            next_page = await get_next_page_element()
            if not next_page:
                return

            next_url = ""
            if isinstance(next_page, ElementHandle):
                await next_page.click(timeout=timeout)
                await self.page.wait_for_timeout(timeout)
                next_url = self.page.url

            elif isinstance(next_page, str):
                next_url = next_page
                if next_url.startswith("?"):
                    # TODO: merge query params
                    next_url = self.page.url.split("?")[0] + next_url

                await self.page.goto(normalize_url(next_url, self.page.url))
                await self.page.wait_for_timeout(timeout)

            if next_url:
                await self._notify_observers("on_paginate", next_url)
                if not self._scraper:
                    return
                await self._scraper(
                    self, next_url, self._context
                )  # TODO: eventually fix this to not be recursive
        except PlaywrightTimeoutError as e:
            raise TimeoutError(
                f"{e.args[0]} You may increase the timeout by passing `timeout` in ms to `SDK.paginate`. Alternatively, this may mean that the next page element or URL was not found and pagination is complete."
            ) from e
        except (TimeoutError, AttributeError, StopAsyncIteration):
            return

    async def capture_url(
        self,
        clickable: ElementHandle,
        resource_type: ResourceType = "document",
        timeout: Optional[int] = 10000,
    ) -> URL | None:
        """
        Capture the url of a click event. This will click the element and return the url
        via network request interception. This is useful for capturing urls that are
        generated dynamically (eg: redirects to document downloads).

        :param clickable: the element to click
        :param resource_type: the type of resource to capture
        :param timeout: the time to wait for the new page to open (in ms)
        :return url: the url of the captured resource or None if no match was found
        :raises ValueError: if more than one page is created by the click event
        """
        async with ResourceRequestHandler(
            self.page, resource_type=resource_type, timeout=timeout
        ) as handler:
            await clickable.click()

        return handler.captured_url()

    async def capture_download(
        self,
        clickable: ElementHandle,
        override_filename: str | None = None,
        override_url: str | None = None,
        timeout: float | None = None,
    ) -> DownloadMeta:
        """
        Capture a download event that gets triggered by clicking an element. This method will:
         - Handle clicking the element
         - Download the resulting file
         - Apply download handling logic and build a download URL
         - Return a download metadata object

        Use this method to manually download dynamic files or files that can only be downloaded in the current browser session.

        :return DownloadMeta: A typed dict containing the download metadata such as the `url` and `filename`
        """

        async with self.page.expect_download(timeout=timeout) as download_info:
            await clickable.click()
        download = await download_info.value

        # Create a temporary file to save the download
        with tempfile.NamedTemporaryFile() as temp_file:
            await download.save_as(temp_file.name)
            with open(temp_file.name, "rb") as f:
                content = f.read()

        res = await self._notify_observers(
            "on_download",
            override_url if override_url else download.url,
            override_filename if override_filename else download.suggested_filename,
            content,
            check_duplication=False,
        )
        return res[0]

    async def capture_html(
        self,
        selector: str = "html",
        exclude_selectors: List[str] | None = None,
        *,
        soup_transform: Optional[Callable[[BeautifulSoup], None]] = None,
        html_converter_type: HTMLConverterType = "markdown",
    ) -> HTMLMetadata:
        """
        Capture and download the html content of the document or a specific element.
        The returned HTML will be cleaned of any excluded elements and will be wrapped in a proper HTML document structure.

        :param selector: CSS selector of element to capture. Defaults to "html" for the document element.
        :param exclude_selectors: List of CSS selectors for elements to exclude from capture.
        :param soup_transform: A function to transform the BeautifulSoup html prior to saving. Use this to remove aspects of the returned content
        :param html_converter_type: Type of HTML converter to use for the inner text. Defaults to "markdown".
        :return: HTMLMetadata containing the `html` of the element, the formatted `text` of the element, along with the `url` and `filename` of the document
        :raises ValueError: If the specified selector doesn't match any element.
        :example:
            >>> meta = await sdk.capture_html(selector="div.content")
            >>> await sdk.save_data({"name": meta["filename"], "text": meta["text"], "download_url": meta["url"]})
        """
        html, text = await self._get_html(
            selector,
            exclude_selectors or [],
            soup_transform or (lambda x: None),
            html_converter_type,
        )

        downloads = await self._notify_observers(
            method="on_download",
            download_url=self.page.url,
            filename=f"{str(uuid.uuid4())}.html",
            content=html.encode("utf-8"),
            check_duplication=False,
        )

        return {
            "url": downloads[0]["url"],
            "filename": downloads[0]["filename"],
            "html": html,
            "text": text,
        }

    async def _get_html(
        self,
        selector: str,
        exclude_selectors: List[str],
        soup_transform: Callable[[BeautifulSoup], None],
        html_converter_type: HTMLConverterType,
    ) -> Tuple[str, str]:
        element = await self.page.query_selector(selector)

        if not element:
            raise ValueError(f"Element not found for selector: {selector}")

        raw_inner_html = await element.inner_html()

        soup = BeautifulSoup(raw_inner_html, "html.parser")
        for selector in exclude_selectors:
            for element_to_remove in soup.select(selector):
                element_to_remove.decompose()

        soup_transform(soup)

        # Ensure HTML doc type is present so the file can be correctly parsed
        if not soup.contents or not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        text = get_html_converter(html_converter_type).convert_soup(soup)

        return str(soup), text

    async def capture_pdf(
        self,
    ) -> DownloadMeta:
        """
        Capture the current page as a pdf and then apply some download handling logic
        from the observer to transform to a usable URL

        :return DownloadMeta: A typed dict containing the download metadata such as the `url` and `filename`
        :example:
            >>> meta = await sdk.capture_pdf()
            >>> await sdk.save_data({"file_name": meta["filename"], "download_url": meta["url"]})
        """
        await self.page.wait_for_timeout(
            1000
        )  # Allow for some extra time for the page to load
        pdf_content = await self.page.pdf()
        file_name = PAGE_PDF_FILENAME
        res = await self._notify_observers(
            "on_download", self.page.url, file_name, pdf_content
        )
        return res[0]

    async def save_cookies(
        self,
        override_cookies: Optional[List[Cookie]] = None,
    ) -> None:
        """
        Save the cookies from the current browser context or use the provided cookies.

        This function retrieves all the cookies from the current browser context if none are provided,
        saves them to the SDK instance, and notifies all observers about the action performed.

        :param override_cookies: Optional list of cookie dictionaries to save. If None, cookies are retrieved from the current page context.
        """
        new_cookies = override_cookies or cast(
            List[Cookie], await self.page.context.cookies()
        )
        new_cookies = [fix_cookie(cookie) for cookie in new_cookies]

        self._saved_cookies = self._saved_cookies + new_cookies

        await self._notify_observers("on_save_cookies", new_cookies)

    async def save_local_storage(
        self,
        override_local_storage: Optional[dict[str, str]] = None,
        override_domain: str | None = None,
        override_path: str | None = None,
    ) -> None:
        """
        Save the local storage from the current browser context or provided local storage.

        This function retrieves all the local storage data from the current page context if none is provided,
        updates the SDK instance with new or updated values, and notifies all observers about the action performed.

        :param override_local_storage: Optional list of local storage items (key-value pairs) to save. If None, local storage is retrieved from the current page context.
        :param override_domain: Optional domain to use for the local storage
        :param override_path: Optional path to use for the local storage
        """
        new_browser_local_storage = override_local_storage or await self.page.evaluate(
            "() => localStorage"
        )

        domain = override_domain or self._domain
        if not domain:
            raise RuntimeError("No domain provided for local storage")

        new_local_storage = [
            LocalStorage(
                domain=domain,
                path=override_path or "/",
                key=key,
                value=new_browser_local_storage[key],
            )
            for key in new_browser_local_storage.keys()
        ]

        self._saved_local_storage = self._saved_local_storage + new_local_storage

        await self._notify_observers("on_save_local_storage", new_local_storage)

    async def solve_captchas(self) -> None:
        """
        Check for captchas on the page and solve them.
        """
        await self._notify_observers(
            "on_check_and_solve_captchas", self.page, check_duplication=False
        )

    async def _notify_observers(
        self,
        method: ObservationTrigger,
        *args: Any,
        check_duplication: bool = True,
        **kwargs: Any,
    ) -> Any:
        """
        Notify all observers of an event. This will call the method on each observer that is subscribed. Note that
        the first observer is the stop pagination observer, so it will always be called separately so that we can stop
        pagination if needed.

        :param method: observation trigger
        :param args: arguments to pass to the method
        :param kwargs: keyword arguments to pass to the method
        :return: the result of the method call
        """
        duplicated = False
        if check_duplication:
            duplicated = getattr(self._deduper, method)(*args, **kwargs)
        if not duplicated:
            return await asyncio.gather(
                *[getattr(o, method)(*args, **kwargs) for o in self._observers]
            )

    @staticmethod
    async def run(
        scraper: AsyncScraperType,
        url: str | Path,
        schema: Schema | None = None,
        context: Optional[Context] = None,
        setup: Optional[SetupType] = None,
        harness: WebHarness = playwright_harness,
        evaluator: Optional[ExpressionEvaluator] = None,
        observer: Optional[OutputObserver | List[OutputObserver]] = None,
        goto_error_handler: Callable[
            [str, int, dict[str, str]], Awaitable[None]
        ] = default_error_callback,
        **harness_options: Unpack[HarnessOptions],
    ) -> "SDK":
        """
        Convenience method for running a scraper. This will launch a browser and
        invoke the scraper function.
        :param scraper: scraper to run
        :param url: starting url to run the scraper on
        :param schema: schema used to validate output correctness
        :param context: additional context to pass to the scrapers
        :param setup: setup function to run before the scraper
        :param harness: the harness to use for the browser
        :param evaluator: expression evaluator to use for the scraper
        :param observer: observer to use for the scraper
        :return none: everything should be saved to the database or file
        """
        domain = getattr(scraper, "domain", None)
        stage = getattr(scraper, "stage", None)
        observer = observer or getattr(scraper, "observer", None)
        context = context or {}

        harness_options.setdefault("headers", getattr(scraper, "extra_headers", None))  # type: ignore

        if isinstance(url, Path):
            url = f"file://{url.resolve()}"

        async with harness(**harness_options) as page_factory:
            page = await page_factory()
            sdk = SDK(
                page,
                domain=domain,
                stage=stage,
                observer=observer,
                scraper=scraper,
                context=context,
                schema=schema,
                evaluator=evaluator,
            )
            if setup:
                await setup(sdk)

            if not harness_options.get("disable_go_to_url", False):
                response = await page.goto(url)
                if response.status >= 400:
                    await goto_error_handler(url, response.status, response.headers)
            elif isinstance(page, SoupPage):
                page.url = url
            await scraper(sdk, url, context)

        return sdk

    async def get_content_type(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.head(normalize_url(url, self.page.url)) as response:
                return response.headers.get("Content-Type", "")

    @staticmethod
    async def run_from_file(
        scraper: AsyncScraperType,
        schema: Schema,
        setup: Optional[SetupType] = None,
        **harness_options: Unpack[HarnessOptions],
    ) -> "SDK":
        """
        Convenience method for running a detail scraper from file. This will load
        the listing data from file and pass it to the scraper.

        :param scraper: the scraper to run (function)
        :param schema: schema used to validate output correctness
        :param headless: whether to run the browser headless
        :param cdp_endpoint: endpoint to connect to the browser (if using a remote browser)
        :param proxy: proxy to use for the browser
        :param setup: optional setup
        :return: None: the scraper should save data to the database or file
        """
        domain: str = getattr(scraper, "domain", "")
        stage: str = getattr(scraper, "stage", "")
        headers: dict[str, str] = getattr(scraper, "extra_headers", {})
        observer: Optional[OutputObserver] = getattr(scraper, "observer", None)

        if stage != "detail" and stage != "listing":
            raise ValueError("Only listing / detail scrapers can be run from file")

        tracker = FileDataTracker(domain, stage)

        prev = "listing" if stage == "detail" else "category"
        file_path = tracker.get_storage_filepath(prev)

        if not file_path.exists():
            raise ValueError(
                f"Could not find {file_path}."
                f" No listing data found for this domain. Run the listing scraper first."
            )

        listing_data = tracker.load_data(domain, prev)
        async with playwright_harness(**harness_options) as page_factory:
            page = await page_factory()
            for listing in listing_data:
                sdk = SDK(
                    page,
                    domain=domain,
                    stage=stage,  # type: ignore
                    observer=observer,
                    scraper=scraper,
                    schema=schema,
                )
                if setup:
                    await setup(sdk)

                if headers:
                    await page.set_extra_http_headers(headers)
                await page.goto(listing["url"])
                await scraper(
                    sdk,
                    listing["url"],
                    listing["context"],
                )

        return sdk

    @staticmethod
    def scraper(
        domain: str,
        stage: Stage,
        observer: Optional[OutputObserver | List[OutputObserver]] = None,
    ) -> Callable[[AsyncScraperType], AsyncScraperType]:
        """
        Decorator for scrapers. This will add the domain and stage to the function.
        All scrapers should be decorated with this decorator.
        :param domain: the url that the scraper is for (eg: https://example.org)
        :param stage: the stage of the scraper (eg: listing or detail)
        :param observer: the observer to use for the scraper
        :return: the decorated function
        """
        if not observer:
            observer = [
                LocalStorageObserver(FileDataTracker(domain=domain, stage=stage)),
                LoggingObserver(),
            ]
        if not isinstance(observer, list):
            observer = [observer]

        def decorator(func: AsyncScraperType) -> AsyncScraperType:
            @wraps(func)
            async def wrapper(sdk: "SDK", url: URL, context: Context) -> None:
                return await func(sdk, url, context)

            wrapper.domain = domain  # type: ignore
            wrapper.stage = stage  # type: ignore
            wrapper.observer = observer  # type: ignore
            return wrapper

        return decorator

    @staticmethod
    def with_headers(
        headers: dict[str, str],
    ) -> Callable[[AsyncScraperType], AsyncScraperType]:
        """
        Decorator for scrapers. This will add the headers to the function.
        All scrapers should be decorated with this decorator.
        :param headers: the headers to use for the scraper
        :return: the decorated function
        """

        def decorator(func: AsyncScraperType) -> AsyncScraperType:
            @wraps(func)
            async def wrapper(sdk: "SDK", url: URL, context: Context) -> None:
                return await func(sdk, url, context)

            wrapper.extra_headers = headers  # type: ignore
            return wrapper

        return decorator


PAGE_PDF_FILENAME = "reworkd_page_pdf.pdf"

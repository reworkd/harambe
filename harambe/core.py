import asyncio
import tempfile
import uuid
from functools import wraps
from typing import Callable, List, Optional, Protocol, Union, Awaitable

import aiohttp
from playwright.async_api import (
    Page,
    async_playwright,
    ElementHandle,
)
from playwright_stealth import stealth_async

from harambe.handlers import (
    ResourceRequestHandler,
    ResourceType,
    UnnecessaryResourceHandler,
)
from harambe.normalize_url import normalize_url
from harambe.observer import (
    LocalStorageObserver,
    LoggingObserver,
    OutputObserver,
    DownloadMeta,
)
from harambe.tracker import FileDataTracker
from harambe.types import URL, AsyncScraperType, Context, ScrapeResult, Stage


class AsyncScraper(Protocol):
    """
    Protocol that all classed based scrapers should implement.
    Note that scrapers in harambe should be functions, not classes.
    """

    async def scrape(self, sdk: "SDK", url: URL, context: Context) -> None:
        ...


class SDK:
    """
    All Harambe scrapers should use this SDK to scrape data. It provides
    a number of useful methods for saving data and enqueuing urls to be scraped later.

    Harambe scrapers should be invoked using the SDK.run (for listing type scrapers) or
    SDK.run_from_file (for detail type scrapers) methods.
    """

    def __init__(
        self,
        page: Page,
        run_id: Optional[str] = None,
        domain: Optional[str] = None,
        stage: Optional[Stage] = None,
        observer: Optional[Union[OutputObserver, List[OutputObserver]]] = None,
        scraper: Optional[AsyncScraperType] = None,
        context: Optional[Context] = None,
    ):
        self.page = page
        self._id = run_id or uuid.uuid4()
        self._domain = domain
        self._stage = stage
        self._scraper = scraper
        self._context = context or {}

        if not observer:
            observer = [LoggingObserver()]

        if not isinstance(observer, list):
            observer = [observer]

        self._observers = observer

    async def save_data(self, *data: ScrapeResult) -> None:
        """
        Save scraped data. This will be passed to the on_save_data callback.
        Generally, this should only be called on the detail page.

        :param data: one or more dicts of details to save
        """
        url = self.page.url
        for d in data:
            d["__url"] = url
            await asyncio.gather(*[o.on_save_data(d) for o in self._observers])

    async def enqueue(self, *urls: URL, context: Optional[Context] = None) -> None:
        """
        Enqueue url to be scraped. This will be passed to the on_enqueue callback.
        This should be called on the listing page. It will save the url and context
        so that the detail page can be scraped later.

        :param urls: urls to enqueue
        :param context: additional context to pass to the detail page
        """
        context = context or {}
        context["__url"] = self.page.url

        for url in urls:
            await asyncio.gather(
                *[o.on_queue_url(url, context) for o in self._observers]
            )

    async def paginate(
        self,
        get_next_page_element: Callable[..., Awaitable[URL | ElementHandle | None]],
        timeout: int = 5000,
    ) -> None:
        """
        Navigate to the next page of a listing.

        :param sleep: seconds to sleep for before continuing
        :param get_next_page_element: the url or ElementHandle of the next page
        """
        try:
            next_page = await get_next_page_element()
            if not next_page:
                return

            next_url = ""
            if isinstance(next_page, ElementHandle):
                await next_page.click(timeout=timeout)
                next_url = self.page.url

            elif isinstance(next_page, str):
                next_url = next_page
                if next_url.startswith("?"):
                    # TODO: merge query params
                    next_url = self.page.url.split("?")[0] + next_url
                    await self.page.goto(next_url)

            if next_url:
                await self._scraper(
                    self, next_url, self._context
                )  # TODO: eventually fix this to not be recursive
        except TimeoutError:
            return

    async def capture_url(
        self, clickable: ElementHandle, resource_type: ResourceType = "document"
    ) -> URL | None:
        """
        Capture the url of a click event. This will click the element and return the url
        via network request interception. This is useful for capturing urls that are
        generated dynamically (eg: redirects to document downloads).

        :param clickable: the element to click
        :param resource_type: the type of resource to capture
        :return url: the url of the captured resource or None if no match was found
        :raises ValueError: if more than one request matches
        """
        async with ResourceRequestHandler(
            self.page, resource_type=resource_type
        ) as handler:
            await clickable.click()

        return handler.captured_url()

    async def capture_download(
        self,
        clickable: ElementHandle,
    ) -> DownloadMeta:
        """
        Capture the download of a click event. This will click the element, download the resulting file
        and apply some download handling logic from the observer to transform to a usable URL
        """

        async with self.page.expect_download() as download_info:
            await clickable.click()
        download = await download_info.value

        # Create a temporary file to save the download
        with tempfile.NamedTemporaryFile() as temp_file:
            await download.save_as(temp_file.name)
            with open(temp_file.name, "rb") as f:
                content = f.read()

        res = await asyncio.gather(
            *[
                o.on_download(download.url, download.suggested_filename, content)
                for o in self._observers
            ]
        )
        return res[0]

    async def capture_pdf(
        self,
    ) -> DownloadMeta:
        """
        Capture the current page as a pdf and then apply some download handling logic
        from the observer to transform to a usable URL
        """
        await self.page.wait_for_timeout(
            1000
        )  # Allow for some extra time for the page to load
        pdf_content = await self.page.pdf()
        file_name = PAGE_PDF_FILENAME
        res = await asyncio.gather(
            *[
                o.on_download(self.page.url, file_name, pdf_content)
                for o in self._observers
            ]
        )
        return res[0]

    @staticmethod
    async def run(
        scraper: AsyncScraperType,
        url: Optional[str] = None,
        context: Optional[Context] = None,
        headless: bool = False,
    ) -> None:
        """
        Convenience method for running a scraper. This will launch a browser and
        invoke the scraper function.
        :param scraper: scraper to run
        :param url: starting url to run the scraper on
        :param context: additional context to pass to the scraper
        :param headless: whether to run the browser headless
        :return none: everything should be saved to the database or file
        """
        domain = getattr(scraper, "domain", None)
        stage = getattr(scraper, "stage", None)
        observer = getattr(scraper, "observer", None)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            ctx = await browser.new_context(
                viewport={"width": 1280, "height": 1024},
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            )
            ctx.set_default_timeout(60000)

            await ctx.route("**/*", UnnecessaryResourceHandler().handle)

            await ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = await ctx.new_page()
            await stealth_async(page)

            try:
                await page.goto(url)
                await scraper(
                    SDK(
                        page,
                        domain=domain,
                        stage=stage,
                        observer=observer,
                        scraper=scraper,
                        context=context,
                    ),
                    url,
                    context,
                )
            except Exception as e:
                # TODO: Fix path for non Mr. Watkins
                await ctx.tracing.stop(path="trace.zip")
                await browser.close()
                raise e
            else:
                await ctx.tracing.stop(path="trace.zip")
                await browser.close()

    async def get_content_type(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.head(normalize_url(url, self.page.url)) as response:
                return response.headers.get("Content-Type", "")

    @staticmethod
    async def run_from_file(scraper: AsyncScraperType, headless: bool = False) -> None:
        """
        Convenience method for running a detail scraper from file. This will load
        the listing data from file and pass it to the scraper.

        :param scraper: the scraper to run (function)
        :param headless: whether to run the browser headless
        :return: None: the scraper should save data to the database or file
        """
        domain = getattr(scraper, "domain", None)
        stage = getattr(scraper, "stage", None)
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
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            ctx = await browser.new_context()
            page = await ctx.new_page()
            await stealth_async(page)

            for listing in listing_data:
                await scraper(
                    SDK(
                        page,
                        domain=domain,
                        stage=stage,
                        observer=observer,
                        scraper=scraper,
                    ),
                    listing["url"],
                    listing["context"],
                )

            await browser.close()

    @staticmethod
    def scraper(
        domain: str, stage: Stage
    ) -> Callable[[AsyncScraperType], AsyncScraperType]:
        """
        Decorator for scrapers. This will add the domain and stage to the function.
        All scrapers should be decorated with this decorator.
        :param domain: the url that the scraper is for (eg: https://example.org)
        :param stage: the stage of the scraper (eg: listing or detail)
        :return: the decorated function
        """

        def decorator(func: AsyncScraperType) -> AsyncScraperType:
            @wraps(func)
            async def wrapper(sdk: "SDK", url: URL, context: Context) -> None:
                return await func(sdk, url, context)

            wrapper.domain = domain
            wrapper.stage = stage
            wrapper.observer = [LocalStorageObserver(domain, stage), LoggingObserver()]
            return wrapper

        return decorator


PAGE_PDF_FILENAME = "reworkd_page_pdf.pdf"

import functools
import re
from typing import Callable, List, Optional, ParamSpec, TypeVar, Union
from urllib.parse import urljoin

from playwright.async_api import Locator, Page

PageLocator = Union[Locator, Page]


class PlaywrightUtils:
    @staticmethod
    async def parse_by_regex(page: PageLocator, selector: str) -> str:
        return await parse_by_regex(page, selector)  # type: ignore

    @staticmethod
    async def parse_attr(page: PageLocator, selector: str) -> str:
        return await parse_attr(page, selector)

    @staticmethod
    async def get_texts(page: PageLocator, selector: str) -> List[str]:
        return await get_texts(page, selector)

    @staticmethod
    async def get_text(page: PageLocator, selector: str) -> str:
        return await get_text(page, selector)

    @staticmethod
    async def get_attrs(page: PageLocator, selector: str, attr: str) -> List[str]:
        return await get_attrs(page, selector, attr)

    @staticmethod
    async def get_attr(page: PageLocator, selector: str, attr: str) -> str:
        return await get_attr(page, selector, attr)

    @staticmethod
    async def get_links(page: PageLocator, selector: str) -> List[str]:
        return await get_links(page, selector)

    @staticmethod
    async def get_link(page: PageLocator, selector: str) -> str:
        return await get_link(page, selector)


async def parse_by_regex(page: PageLocator, selector: str) -> Optional[str]:
    page_source = await (
        page.evaluate("(element) => element.outerHTML")
        if isinstance(page, Locator)
        else page.content()
    )

    data = re.findall(selector, page_source)
    return data[0] if data else None


async def parse_attr(page: PageLocator, selector: str) -> str:
    xpath, attr = selector.split(r"/@")
    data = await get_attr(page, xpath, attr)
    if data.startswith("/"):
        data = urljoin(page.url, data)  # type: ignore
    return data


async def get_texts(page: PageLocator, selector: str) -> List[str]:
    elements = await page.locator(selector).all()
    data = [await el.text_content() for el in elements]
    return [d.strip() for d in data if d]


async def get_text(page: PageLocator, selector: str) -> str:
    data = await get_texts(page, selector)
    return data[0] if data else ""


async def get_attrs(page: PageLocator, selector: str, attr: str) -> List[str]:
    elements = await page.locator(selector).all()
    data = [await el.get_attribute(attr) for el in elements]
    return [d.strip() for d in data if d]


async def get_attr(page: PageLocator, selector: str, attr: str) -> str:
    data = await get_attrs(page, selector, attr)
    return data[0] if data else ""


# TODO: edge case where page is a Locator and url is not set
async def get_links(page: PageLocator, selector: str) -> List[str]:
    urls = await get_attrs(page, selector, attr="href")
    if isinstance(page, Locator):
        setattr(page, "url", "")
    return [urljoin(page.url, url) for url in urls if url]  # type: ignore


async def get_link(page: PageLocator, selector: str) -> str:
    data = await get_links(page, selector)
    return data[0] if data else ""


P = ParamSpec("P")
T = TypeVar("T")


def swallow_exceptions(func: Callable[P, T]) -> Callable[P, Optional[T]]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Exception swallowed in {func.__name__}: {e}")
            return None

    return wrapper

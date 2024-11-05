from typing import Any, Optional

from bs4 import BeautifulSoup, Tag

# noinspection PyProtectedMember
from curl_cffi.requests import AsyncSession, HeaderTypes

from harambe.contrib.soup.tracing import Tracer
from harambe.contrib.types import AbstractElementHandle, AbstractPage, Selectable, T


class SoupElementHandle(AbstractElementHandle, Selectable["SoupElementHandle"]):
    def __init__(self, tag: Tag) -> None:
        self._tag = tag

    @classmethod
    def from_tag(cls, tag: Tag | None) -> Optional["SoupElementHandle"]:
        return cls(tag) if tag else None

    @classmethod
    def from_tags(cls, tag: list[Tag]) -> list["SoupElementHandle"]:
        return [cls(t) for t in tag]

    async def inner_text(self) -> str:
        return self._tag.get_text()

    async def inner_html(self) -> str:
        return self._tag.decode_contents()

    async def text_content(self) -> str:
        return await self.inner_text()

    async def get_attribute(self, name: str) -> str:
        return self._tag.get(name)

    async def query_selector_all(self, selector: str) -> list["SoupElementHandle"]:
        return self.from_tags(self._tag.select(selector))

    async def query_selector(self, selector: str) -> Optional["SoupElementHandle"]:
        return self.from_tag(self._tag.select_one(selector))

    async def click(self) -> None:
        raise NotImplementedError()

    async def wait_for_selector(self, selector: str, **kwargs: Any) -> None:
        pass


class SoupPage(AbstractPage[SoupElementHandle]):
    _soup: BeautifulSoup
    _url: str

    def __init__(
        self,
        session: AsyncSession,
        extra_headers: Optional[HeaderTypes] = None,
        tracer: Tracer = Tracer(),
    ) -> None:
        self._session = session
        self._extra_headers = extra_headers
        self._tracer = tracer
        self._url = "about:blank"

    @property
    def tracing(self) -> Tracer:
        return self._tracer

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value

    async def goto(self, url: str, **kwargs: Any) -> None:
        res = await self._session.get(
            url, headers=self._extra_headers, impersonate="chrome"
        )
        self._tracer.log_request(res)
        self._url = res.url
        self._soup = BeautifulSoup(res.text, "html.parser")

    async def query_selector_all(self, selector: str) -> list[SoupElementHandle]:
        return SoupElementHandle.from_tags(self._soup.select(selector))

    async def query_selector(self, selector: str) -> SoupElementHandle | None:
        return SoupElementHandle.from_tag(self._soup.select_one(selector))

    def locator(self, selector: str) -> "SoupLocator":
        return SoupLocator(selector, self)

    async def inner_text(self, selector: str) -> str | None:
        if el := await self.query_selector(selector):
            return await el.inner_text()

        return None

    async def wait_for_timeout(self, timeout: int) -> None:
        pass

    async def content(self) -> str:
        return str(self._soup)

    async def text_content(self, selector: str, **kwargs: Any) -> str | None:
        if el := await self.query_selector(selector):
            return await el.text_content()

        return None

    async def wait_for_selector(self, selector: str, **kwargs: Any) -> None:
        pass

    async def set_extra_http_headers(self, headers: dict[str, str]) -> None:
        self._extra_headers = headers

    async def set_default_timeout(self, timeout: float) -> None:
        pass

    async def wait_for_load_state(self, **kwargs: Any) -> None:
        pass

    async def title(self) -> str | None:
        title = self._soup.title
        if title:
            return title.string
        return None


class SoupLocator:
    def __init__(self, selector: str, page: SoupPage) -> None:
        self._selector = selector
        self._page = page

    async def all(self) -> list[SoupElementHandle]:
        return await self._page.query_selector_all(self._selector)

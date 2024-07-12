from typing import Any, Optional

from bs4 import Tag, BeautifulSoup

# noinspection PyProtectedMember
from curl_cffi.requests import AsyncSession, HeaderTypes

from harambe.contrib.types import AbstractElementHandle, Selectable, AbstractPage


class SoupElementHandle(AbstractElementHandle, Selectable["SoupElementHandle"]):
    def __init__(self, tag: Tag) -> None:
        self._tag = tag

    @classmethod
    def from_tags(cls, tag: list[Tag]) -> list["SoupElementHandle"]:
        return [cls(t) for t in tag]

    async def inner_text(self) -> str:
        return self._tag.get_text()

    async def get_attribute(self, name: str) -> str:
        return self._tag.get(name)

    async def query_selector_all(self, selector: str) -> list["SoupElementHandle"]:
        return self.from_tags(self._tag.select(selector))

    async def query_selector(self, selector: str) -> "SoupElementHandle":
        return SoupElementHandle(self._tag.select_one(selector))

    async def click(self) -> None:
        raise NotImplementedError()

    async def wait_for_selector(self, selector: str, **kwargs: Any) -> None:
        pass


class SoupPage(AbstractPage[SoupElementHandle]):
    _soup: BeautifulSoup
    _url: str

    def __init__(
        self, session: AsyncSession, extra_headers: Optional[HeaderTypes] = None
    ) -> None:
        self._session = session
        self._extra_headers = extra_headers

    @property
    def url(self) -> str:
        return self._url

    async def goto(self, url: str) -> None:
        res = await self._session.get(url, headers=self._extra_headers)
        self._url = res.url
        self._soup = BeautifulSoup(res.text, "html.parser")

    async def query_selector_all(self, selector: str) -> list[SoupElementHandle]:
        return SoupElementHandle.from_tags(self._soup.select(selector))

    async def query_selector(self, selector: str) -> SoupElementHandle:
        return SoupElementHandle(self._soup.select_one(selector))

    async def wait_for_timeout(self, timeout: int) -> None:
        pass

    async def content(self) -> str:
        return str(self._soup)

    async def wait_for_selector(self, selector: str, **kwargs: Any) -> None:
        pass

    async def set_extra_http_headers(self, headers: dict[str, str]) -> None:
        self._extra_headers = headers

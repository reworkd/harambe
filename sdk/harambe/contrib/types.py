import abc

# noinspection PyUnresolvedReferences,PyProtectedMember
from contextlib import _AsyncGeneratorContextManager
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar

T = TypeVar("T", bound="AbstractElementHandle")
WebHarness = Callable[
    ..., _AsyncGeneratorContextManager[Callable[[], Awaitable["AbstractPage[Any]"]]]
]


class AbstractElementHandle(abc.ABC):
    @abc.abstractmethod
    async def inner_text(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def text_content(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_attribute(self, name: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def click(self) -> None:
        raise NotImplementedError()


class Selectable(Generic[T], abc.ABC):
    @abc.abstractmethod
    async def query_selector_all(self, selector: str) -> list[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def query_selector(self, selector: str) -> T | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def wait_for_selector(self, selector: str, **kwargs: Any) -> None:
        raise NotImplementedError()


class AbstractPage(Selectable[T], abc.ABC):
    @property
    @abc.abstractmethod
    def url(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def goto(self, url: str, **kwargs: Any) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def wait_for_timeout(self, timeout: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def content(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def text_content(self, selector: str, **kwargs: Any) -> Optional[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def set_extra_http_headers(self, headers: dict[str, str]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def set_default_timeout(self, timeout: float) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def locator(self, selector: str) -> T | None:
        raise NotImplementedError()

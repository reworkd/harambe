from abc import abstractmethod
from typing import runtime_checkable, Protocol, Any

from harambe_core.types import URL, Context, Options, Cookie, LocalStorage


@runtime_checkable
class OutputObserver(Protocol):
    @abstractmethod
    async def on_save_data(self, data: dict[str, Any]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        raise NotImplementedError()

    @abstractmethod
    async def on_paginate(self, next_url: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_save_cookies(self, cookies: list[Cookie]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_save_local_storage(self, local_storage: list[LocalStorage]) -> None:
        raise NotImplementedError()

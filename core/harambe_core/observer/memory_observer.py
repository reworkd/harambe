from typing import Any, List, Tuple
from urllib.parse import quote

from harambe_core.types import URL, Context, Options, Cookie, LocalStorage
from .base import OutputObserver
from .types import DownloadMeta


class InMemoryObserver(OutputObserver):
    def __init__(self) -> None:
        self._data: List[dict[str, Any]] = []
        self._urls: List[Tuple[URL, Context, Options]] = []
        self._files: List[Tuple[str, bytes]] = []
        self._cookies: List[Cookie] = []
        self._local_storage: List[LocalStorage] = []

    async def on_save_data(self, data: dict[str, Any]) -> None:
        self._data.append(data)

    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        self._urls.append((url, context, options))

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        self._files.append((filename, content))
        return {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }

    async def on_paginate(self, next_url: str) -> None:
        pass

    async def on_save_cookies(self, cookies: list[Cookie]) -> None:
        self._cookies.extend(cookies)

    async def on_check_and_solve_captchas(self, page: "Page") -> None:
        pass

    async def on_save_local_storage(self, local_storage: list[LocalStorage]) -> None:
        self._local_storage.extend(local_storage)

    @property
    def data(self) -> List[dict[str, Any]]:
        return self._data

    @property
    def urls(self) -> List[Tuple[URL, Context, Options]]:
        return self._urls

    @property
    def files(self) -> List[Tuple[str, bytes]]:
        return self._files

    @property
    def cookies(self) -> List[Cookie]:
        return self._cookies

    @property
    def local_storage(self) -> List[LocalStorage]:
        return self._local_storage

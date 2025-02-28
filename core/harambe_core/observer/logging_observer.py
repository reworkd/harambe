from pprint import pprint
from typing import List
from urllib.parse import quote

from harambe_core.types import Cookie, LocalStorage, URL, Context, Options, ScrapeResult
from .base import OutputObserver
from .types import DownloadMeta


class LoggingObserver(OutputObserver):
    async def on_save_data(self, data: ScrapeResult) -> None:
        pprint(data, width=240)

    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        print(f"Enqueuing: {url} with context {context} and options {options}")

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        print(f"Downloading file: {filename}")
        return {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }

    async def on_paginate(self, next_url: str) -> None:
        pass

    async def on_save_cookies(self, cookies: List[Cookie]) -> None:
        print(f"Cookies saved : {cookies}")

    async def on_save_local_storage(self, local_storage: List[LocalStorage]) -> None:
        print(f"Local Storage saved : {local_storage}")

    async def on_check_and_solve_captchas(self, page: "Page") -> None:
        pass

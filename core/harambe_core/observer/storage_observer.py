from abc import ABC, abstractmethod
from typing import Any, List
from urllib.parse import quote

from harambe_core.types import URL, Context, Options, Cookie, LocalStorage
from .base import OutputObserver
from .types import DownloadMeta


class DataTracker(ABC):
    @abstractmethod
    def save_data(self, new_data: List[dict[str, Any]]) -> None:
        """Append data for a domain and stage to a JSON file"""
        raise NotImplementedError()

    @abstractmethod
    def load_data(self, url: str, stage: str) -> List[dict[str, Any]]:
        """Load data for a domain and stage from a JSON file"""
        raise NotImplementedError()

    @abstractmethod
    def visit(self, url: str) -> None:
        """Mark the url as visited and save to the domain file"""
        raise NotImplementedError()

    @abstractmethod
    def has_been_visited(self, url: str) -> bool:
        """Check if the url has been visited"""
        raise NotImplementedError()


class LocalStorageObserver(OutputObserver):
    def __init__(self, tracker: DataTracker):
        self._tracker = tracker

    async def on_save_data(self, data: dict[str, Any]) -> None:
        self._tracker.save_data(data)

    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        self._tracker.save_data({"url": url, "context": context, "options": options})

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> DownloadMeta:
        data: DownloadMeta = {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }
        self._tracker.save_data(data)  # type: ignore
        return data

    async def on_paginate(self, next_url: str) -> None:
        pass

    async def on_save_cookies(self, cookies: List[Cookie]) -> None:
        self._tracker.save_data({"cookies": cookies})

    async def on_save_local_storage(self, local_storage: List[LocalStorage]) -> None:
        self._tracker.save_data({"local_storage": local_storage})

    async def on_check_and_solve_captchas(self, page: "Page") -> None:
        pass

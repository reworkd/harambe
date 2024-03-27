import hashlib
import json
from abc import abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Protocol,
    Tuple,
    runtime_checkable,
    TypedDict,
    Literal,
)
from urllib.parse import quote

from harambe.tracker import FileDataTracker
from harambe.types import URL, Context, Stage


ObservationTrigger = Literal[
    "on_save_data", "on_queue_url", "on_download", "on_paginate"
]


@runtime_checkable
class OutputObserver(Protocol):
    @abstractmethod
    async def on_save_data(self, data: Dict[str, Any]):
        raise NotImplementedError()

    @abstractmethod
    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        raise NotImplementedError()

    @abstractmethod
    async def on_paginate(self, next_url: str) -> None:
        raise NotImplementedError()


class LoggingObserver(OutputObserver):
    async def on_save_data(self, data: Dict[str, Any]):
        print(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        print(f"Enqueuing: {url} with context {context}")

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        print(f"Downloading file: {filename}")  # TODO: use logger
        return {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }

    async def on_paginate(self, next_url: str) -> None:
        pass


class LocalStorageObserver(OutputObserver):
    def __init__(self, domain: str, stage: Stage):
        self._tracker = FileDataTracker(domain, stage)

    async def on_save_data(self, data: Dict[str, Any]) -> None:
        self._tracker.save_data(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        self._tracker.save_data({"url": url, "context": context})

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        data = {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }
        self._tracker.save_data(data)
        return data

    async def on_paginate(self, next_url: str) -> None:
        pass


class InMemoryObserver(OutputObserver):
    def __init__(self):
        self._data: List[Dict[str, Any]] = []
        self._urls: List[Tuple[URL, Context]] = []
        self._files: List[Tuple[str, bytes]] = []

    async def on_save_data(self, data: Dict[str, Any]) -> None:
        self._data.append(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        self._urls.append((url, context))

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        data = {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }
        self._files.append((filename, content))
        return data

    async def on_paginate(self, next_url: str) -> None:
        pass

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._data

    @property
    def urls(self) -> List[Tuple[URL, Context]]:
        return self._urls

    @property
    def files(self) -> List[Tuple[str, bytes]]:
        return self._files


class DuplicateHandler:
    def __init__(self):
        self._saved_data: set[bytes] = set()
        self.rows_on_page = 0
        self.previously_saved_rows_on_page = 0

    async def on_save_data(self, data: dict[str, Any]) -> bool:
        return self._add_data(data)

    async def on_queue_url(self, url: URL, context: dict[str, Any]) -> bool:
        return self._add_data(url)

    # noinspection PyTypeChecker
    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> bool:
        return self._add_data((download_url, filename))

    async def on_paginate(self, next_url: str) -> bool:
        if self.rows_on_page == self.previously_saved_rows_on_page:
            raise StopAsyncIteration()

        self.rows_on_page = 0
        self.previously_saved_rows_on_page = 0
        return False

    def _add_data(self, data: Any) -> bool:
        self.rows_on_page += 1

        hash_value = self.compute_hash(data)
        if hash_value in self._saved_data:
            self.previously_saved_rows_on_page += 1
            return True  # return True if data is duplicated
        else:
            self._saved_data.add(hash_value)
            return False

    @staticmethod
    def compute_hash(data: Any) -> bytes:
        if isinstance(data, dict):
            data = {k: v for k, v in data.items() if not k.startswith("__")}

        data_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return hashlib.md5(data_str.encode()).digest()


class DownloadMeta(TypedDict):
    url: str
    filename: str

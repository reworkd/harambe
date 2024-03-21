from abc import abstractmethod
from typing import Any, Dict, List, Protocol, Tuple, runtime_checkable, TypedDict
from urllib.parse import quote

from harambe.tracker import FileDataTracker
from harambe.types import URL, Context, Stage


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


class LoggingObserver(OutputObserver):
    # TODO: use logger
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

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._data

    @property
    def urls(self) -> List[Tuple[URL, Context]]:
        return self._urls

    @property
    def files(self) -> List[Tuple[str, bytes]]:
        return self._files


class StopPaginationObserver(OutputObserver):
    def __init__(self):
        self._saved_data = set()

    async def on_save_data(self, data: dict[str, Any]):
        self._add_data(data)

    async def on_queue_url(self, url: URL, context: dict[str, Any]) -> None:
        self._add_data(url)

    async def on_download(self, download_url: str, filename: str, content: bytes) -> "DownloadMeta":
        pass

    def _add_data(self, data: Any):
        # TODO remove __url from data?
        d_set = frozenset(data.items() if isinstance(data, dict) else data)
        if d_set in self._saved_data:
            raise StopAsyncIteration()
        self._saved_data.add(d_set)


class DownloadMeta(TypedDict):
    url: str
    filename: str

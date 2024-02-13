from typing import Any, Dict, List, Protocol, Tuple, runtime_checkable

from harambe.tracker import FileDataTracker
from harambe.types import URL, Context, Stage


@runtime_checkable
class OutputObserver(Protocol):
    async def on_save_data(self, data: Dict[str, Any]):
        raise NotImplementedError()

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        raise NotImplementedError()


class LoggingObserver(OutputObserver):
    # TODO: use logger
    async def on_save_data(self, data: Dict[str, Any]):
        print(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        print(f"Enqueuing: {url} with context {context}")


class LocalStorageObserver(OutputObserver):
    def __init__(self, domain: str, stage: Stage):
        self._tracker = FileDataTracker(domain, stage)

    async def on_save_data(self, data: Dict[str, Any]):
        self._tracker.save_data(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        self._tracker.save_data({"url": url, "context": context})


class InMemoryObserver(OutputObserver):
    def __init__(self):
        self._urls: List[Tuple[URL, Context]] = []
        self._data: List[Dict[str, Any]] = []

    async def on_save_data(self, data: Dict[str, Any]):
        self._data.append(data)

    async def on_queue_url(self, url: URL, context: Dict[str, Any]) -> None:
        self._urls.append((url, context))

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._data

    @property
    def urls(self) -> List[Tuple[URL, Context]]:
        return self._urls

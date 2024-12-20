from abc import abstractmethod
from pprint import pprint
from typing import (
    Any,
    List,
    Literal,
    Protocol,
    Tuple,
    TypedDict,
    runtime_checkable,
)
from urllib.parse import quote

from harambe.tracker import FileDataTracker
from harambe.types import URL, Context, Options, Stage, Cookie, LocalStorage
from playwright.async_api import Page

ObservationTrigger = Literal[
    "on_save_data",
    "on_queue_url",
    "on_download",
    "on_paginate",
    "on_save_cookies",
    "on_save_local_storage",
    "on_check_and_solve_captchas",
]


class DownloadMeta(TypedDict):
    url: str
    filename: str


class HTMLMetadata(DownloadMeta):
    html: str
    text: str


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
    async def on_save_cookies(self, cookies: List[Cookie]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_save_local_storage(self, local_storage: List[LocalStorage]) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def on_check_and_solve_captchas(self, page: Page) -> None:
        raise NotImplementedError()


class LoggingObserver(OutputObserver):
    async def on_save_data(self, data: dict[str, Any]) -> None:
        pprint(data, width=240)

    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        print(f"Enqueuing: {url} with context {context} and options {options}")

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

    async def on_save_cookies(self, cookies: List[Cookie]) -> None:
        print(f"Cookies saved : {cookies}")

    async def on_save_local_storage(self, local_storage: List[LocalStorage]) -> None:
        print(f"Local Storage saved : {local_storage}")

    async def on_check_and_solve_captchas(self, page: Page) -> None:
        pass


class LocalStorageObserver(OutputObserver):
    def __init__(self, domain: str, stage: Stage):
        self._tracker = FileDataTracker(domain, stage)

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

    async def on_check_and_solve_captchas(self, page: Page) -> None:
        pass


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

    async def on_save_cookies(self, cookies: List[Cookie]) -> None:
        self._cookies.extend(cookies)

    async def on_check_and_solve_captchas(self, page: Page) -> None:
        pass

    async def on_save_local_storage(self, local_storage: List[LocalStorage]) -> None:
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

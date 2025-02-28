from typing import Any, Callable, TypeVar, TypedDict
from urllib.parse import quote

from harambe_core.observer import OutputObserver
from harambe_core.types import LocalStorage, Cookie, URL, Context, Options
from .types import DownloadMeta, ObservationTrigger


class Payload(TypedDict):
    type: ObservationTrigger
    data: dict[str, Any] | list[Cookie] | list[LocalStorage]


T = TypeVar("T")

Serializer = Callable[[Payload], T]
Sink = Callable[[T], None]


class SerializationObserver(OutputObserver):
    def __init__(self, sink: Sink, serializer: Serializer) -> None:
        self._publish: Callable[[Payload], None] = lambda x: sink(serializer(x))

    async def on_save_data(self, data: dict[str, Any]) -> None:
        payload: Payload = {"type": "on_save_data", "data": data}

        self._publish(payload)

    async def on_queue_url(self, url: URL, context: Context, options: Options) -> None:
        payload: Payload = {
            "type": "on_queue_url",
            "data": {"url": url, "context": context, "options": options},
        }

        self._publish(payload)

    async def on_download(
        self, download_url: str, filename: str, content: bytes
    ) -> "DownloadMeta":
        payload: Payload = {
            "type": "on_download",
            "data": {
                "download_url": download_url,
                "filename": filename,
                "content": content.decode("utf-8"),
            },
        }

        self._publish(payload)

        return {
            "url": f"{download_url}/{quote(filename)}",
            "filename": filename,
        }

    async def on_paginate(self, next_url: str) -> None:
        pass

    async def on_save_cookies(self, cookies: list[Cookie]) -> None:
        payload: Payload = {"type": "on_save_cookies", "data": cookies}

        self._publish(payload)

    async def on_save_local_storage(self, local_storage: list[LocalStorage]) -> None:
        payload: Payload = {"type": "on_save_local_storage", "data": local_storage}

        self._publish(payload)

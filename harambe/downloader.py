from typing import Protocol, TypedDict

from playwright.async_api import Download


class DownloadMeta(TypedDict):
    url: str
    filename: str


class Downloader(Protocol):
    async def on_download(self, download: Download) -> DownloadMeta:
        raise NotImplementedError()


class LoggingDownloader(Downloader):
    async def on_download(self, download: Download) -> DownloadMeta:
        print("on_download", download)  # TODO: use logger
        return {
            "url": str(await download.path()),
            "filename": download.suggested_filename,
        }

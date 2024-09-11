from .core import PAGE_PDF_FILENAME, SDK, AsyncScraper
from .parser.schemas import Schemas
from .types import AsyncScraperType, ScrapeResult
from .utils import PlaywrightUtils


def save_cookies(page):
    sdk = SDK(page)
    return sdk.save_cookies()


__all__ = [
    "ScrapeResult",
    "Schemas",
    "SDK",
    "PlaywrightUtils",
    "AsyncScraperType",
    "AsyncScraper",
    "PAGE_PDF_FILENAME",
    "save_cookies",
]

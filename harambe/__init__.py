from .core import PAGE_PDF_FILENAME, SDK, AsyncScraper
from .parser.schemas import Schemas
from .types import AsyncScraperType, ScrapeResult
from .utils import PlaywrightUtils
from harambe.observer import (
    LocalStorageObserver,
    LoggingObserver,
)


def save_cookies(page, domain, stage):
    # Initialize SDK with necessary observers
    observers = [LocalStorageObserver(domain, stage), LoggingObserver()]
    sdk = SDK(page, domain=domain, stage=stage, observer=observers)
    return sdk.save_cookies()


__all__ = [
    "ScrapeResult",
    "Schemas",
    "SDK",
    "PlaywrightUtils",
    "AsyncScraperType",
    "AsyncScraper",
    "PAGE_PDF_FILENAME",
    "save_cookies"
]

from typing import Any, Awaitable, Callable, Dict, Literal

Enum = str
URL = str
ScrapeResult = Dict[str, Any]
Context = Dict[str, Any]
Stage = Literal["category", "listing", "detail"]
AsyncScraperType = Callable[["SDK", URL, Context], Awaitable[None]]  # noqa: F821
SetupType = Callable[["SDK"], Awaitable[None]]  # noqa: F821
Schema = Dict[str, Any]

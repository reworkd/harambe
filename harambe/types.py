from typing import Any, Awaitable, Callable, Literal, TypedDict, Optional

Enum = str
URL = str
ScrapeResult = dict[str, Any]
Context = dict[str, Any]
Stage = Literal["category", "listing", "detail"]
AsyncScraperType = Callable[["SDK", URL, Context], Awaitable[None]]  # noqa: F821
SetupType = Callable[["SDK"], Awaitable[None]]  # noqa: F821
Schema = dict[str, Any]


class SetCookieParam(TypedDict, total=False):
    name: str
    value: str
    url: Optional[str]
    domain: Optional[str]
    path: Optional[str]
    expires: Optional[float]
    httpOnly: Optional[bool]
    secure: Optional[bool]
    sameSite: Optional[Literal["Lax", "None", "Strict"]]

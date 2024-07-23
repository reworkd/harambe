from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    NotRequired,
    Optional,
    Sequence,
    TypedDict,
)

from playwright.async_api import ViewportSize

Enum = str
URL = str
ScrapeResult = dict[str, Any]
Context = dict[str, Any]
Options = dict[str, Any]
Stage = Literal["category", "listing", "detail"]
AsyncScraperType = Callable[["SDK", URL, Context], Awaitable[None]]  # type: ignore # noqa: F821
SetupType = Callable[["SDK"], Awaitable[None]]  # type: ignore # noqa: F821
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


class HarnessOptions(TypedDict):
    headless: NotRequired[bool]
    cdp_endpoint: NotRequired[str]
    proxy: NotRequired[str]
    cookies: NotRequired[Sequence[SetCookieParam]]
    headers: NotRequired[dict[str, str]]
    stealth: NotRequired[bool]
    default_timeout: NotRequired[int]
    user_agent: NotRequired[str]
    viewport: NotRequired[ViewportSize]

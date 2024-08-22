from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
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
Callback = Callable[..., Awaitable[None]]
BrowserType = Literal["chromium", "firefox", "webkit"]


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


class HarnessOptions(TypedDict, total=False):
    browser_type: BrowserType
    headless: bool
    stealth: bool
    default_timeout: int
    user_agent: str
    proxy: Optional[str]
    cdp_endpoint: Optional[str]
    cookies: Sequence[SetCookieParam]
    headers: Optional[dict[str, str]]
    viewport: Optional[ViewportSize]
    abort_unnecessary_requests: bool
    disable_go_to_url: bool
    on_start: Optional[Callback]
    on_end: Optional[Callback]

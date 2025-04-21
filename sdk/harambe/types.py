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

# noinspection PyUnresolvedReferences
from harambe_core.types import LocalStorage, Cookie, URL, Context, Options, ScrapeResult

Stage = Literal["category", "listing", "detail"]
AsyncScraperType = Callable[["SDK", URL, Context], Awaitable[None]]  # type: ignore # noqa: F821
SetupType = Callable[["SDK"], Awaitable[None]]  # type: ignore # noqa: F821
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
    # TODO: Replace with UserAgentFactory
    user_agent: str | Callable[[], str | Awaitable[str]]
    proxy: Optional[str]
    cdp_endpoint: Optional[str]
    cookies: Sequence[SetCookieParam]
    local_storage: Sequence[LocalStorage]
    headers: Optional[dict[str, str]]
    viewport: Optional[ViewportSize]
    abort_unnecessary_requests: bool
    disable_go_to_url: bool
    on_start: Optional[Callback]
    on_end: Optional[Callback]
    launch_args: Sequence[str]
    extensions: Sequence[str]
    attach_to_existing_context: bool
    attach_to_existing_page: bool

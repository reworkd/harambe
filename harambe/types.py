from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    Sequence,
    TypedDict,
    NotRequired,
    Required,
)

from playwright.async_api import ViewportSize
from pydantic import ConfigDict

Enum = str
URL = str
ScrapeResult = dict[str, Any]
Context = dict[str, Any]
Options = dict[str, Any]
Stage = Literal["category", "listing", "detail"]
AsyncScraperType = Callable[["SDK", URL, Context], Awaitable[None]]  # type: ignore # noqa: F821
SetupType = Callable[["SDK"], Awaitable[None]]  # type: ignore # noqa: F821
Callback = Callable[..., Awaitable[None]]
BrowserType = Literal["chromium", "firefox", "webkit"]

SchemaFieldType = Literal[
    "string",
    "str",
    "boolean",
    "bool",
    "integer",
    "int",
    "number",
    "float",
    "double",
    "currency",
    "email",
    "enum",
    "array",
    "object",
    "datetime",
    "phone_number",
    "url",
]


class Schema(TypedDict, total=False):
    __config__: NotRequired[ConfigDict]
    type: Required[SchemaFieldType]
    description: NotRequired[str]
    properties: NotRequired[dict[str, "Schema"]]
    items: NotRequired["Schema"]
    variants: NotRequired[Sequence[str]]


Schema.__annotations__["__extra_fields__"] = dict[str, "Schema"]


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


class Cookie(TypedDict):
    name: str
    value: str
    domain: str
    path: str
    expires: int | float
    size: int
    httpOnly: bool
    secure: bool
    session: bool
    sameSite: str

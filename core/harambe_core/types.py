from typing import NotRequired, TypedDict, Required, Sequence, Literal, Any

from pydantic import ConfigDict


URL = str
Context = dict[str, Any]
Options = dict[str, Any]
ScrapeResult = dict[str, Any]

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
    expression: NotRequired[str]
    required: NotRequired[bool]


Schema.__annotations__["__extra_fields__"] = dict[str, "Schema"]


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


class LocalStorage(TypedDict):
    domain: str
    path: str | None
    key: str
    value: str

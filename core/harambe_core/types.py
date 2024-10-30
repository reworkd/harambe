from typing import NotRequired, TypedDict, Required, Sequence, Literal

from pydantic import ConfigDict

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


Schema.__annotations__["__extra_fields__"] = dict[str, "Schema"]

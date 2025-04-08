from typing import Any, List, Optional, Self, Type

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    create_model,
    model_validator,
)

from harambe_core.errors import SchemaValidationError
from harambe_core.parser.constants import RESERVED_PREFIX
from harambe_core.parser.expression import ExpressionEvaluator
from harambe_core.parser.type_currency import ParserTypeCurrency
from harambe_core.parser.type_date import ParserTypeDate
from harambe_core.parser.type_email import ParserTypeEmail
from harambe_core.parser.type_enum import ParserTypeEnum
from harambe_core.parser.type_number import ParserTypeNumber
from harambe_core.parser.type_phone_number import ParserTypePhoneNumber
from harambe_core.parser.type_string import ParserTypeString
from harambe_core.parser.type_url import ParserTypeUrl
from harambe_core.types import Schema, SchemaFieldType


class SchemaParser:
    """
    A schema parser that uses Pydantic models to validate data against a JSON schema
    """

    def __init__(
        self, schema: Schema, evaluator: ExpressionEvaluator | None = None
    ) -> None:
        self._pk_expression = schema.get("$primary_key", None)

        if "$schema" in schema:
            del schema["$schema"]
        if "$primary_key" in schema:
            del schema["$primary_key"]

        if evaluator is None:
            evaluator = ExpressionEvaluator()

        self.evaluator = evaluator
        self.schema = schema
        self.field_types: dict[SchemaFieldType, Any] = {}

    def validate(self, data: dict[str, Any], base_url: str) -> dict[str, Any]:
        # Set these values here for convenience to avoid passing them around. A bit hacky
        self.field_types = self._get_field_types(base_url)
        model = self._schema_to_pydantic_model(self.schema, is_root=True)

        try:
            res = model(**data).model_dump(by_alias=True)
            if self._pk_expression:
                res["$primary_key"] = self.evaluator.evaluate(self._pk_expression, res)
            return res

        except (TypeError, ValidationError) as e:
            raise SchemaValidationError(message=str(e))

    @staticmethod
    def _get_field_types(base_url: str) -> dict[SchemaFieldType, Any]:
        return {
            "string": ParserTypeString,
            "str": ParserTypeString,
            "boolean": bool,
            "bool": bool,
            "integer": int,
            "int": int,
            "number": ParserTypeNumber,
            "float": ParserTypeNumber,
            "double": ParserTypeNumber,
            "currency": ParserTypeCurrency(),
            "email": ParserTypeEmail,
            "enum": ParserTypeEnum,
            "array": list,
            "object": dict[str, Any],
            "datetime": ParserTypeDate(),
            "phone_number": ParserTypePhoneNumber(),
            "url": ParserTypeUrl(base_url=base_url),
        }

    def _items_schema_to_python_type(
        self, items_info: Schema, model_name: str = "DynamicModelItem"
    ) -> Type[Any]:
        """
        Convert a JSON schema's items property to a Python type
        """
        item_type = items_info.get("type")
        if item_type is None:
            raise ValueError(f"Item type for array `{model_name}` is missing")

        if item_type == "object":
            return self._schema_to_pydantic_model(
                items_info.get("properties", {}),
                model_name=f"{model_name}Object",
                is_root=False,
            )

        if item_type == "array":
            return List[  # type: ignore
                self._items_schema_to_python_type(
                    items_info.get("items", {}),
                    model_name=f"{model_name}Item",
                )
            ]

        # Every enum has its own unique variants
        if item_type == "enum":
            return self._get_type(item_type, required=True)(items_info["variants"])

        return self._get_type(item_type, required=True)

    def _schema_to_pydantic_model(
        self,
        schema: Schema,
        model_name: str = "DynamicModel",
        required: bool = True,
        is_root: bool = True,
    ) -> Type[BaseModel]:
        """
        Convert a JSON schema to a Pydantic model dynamically. All fields are optional
        """
        fields = {}
        computed_fields = {}

        for field_name, field_info in schema.items():
            if field_name == "__config__":
                continue

            field_serialization_alias = None
            if field_name.startswith("model_"):
                field_serialization_alias = field_name
                field_name = RESERVED_PREFIX + field_name

            field_description = field_info.get("description", None)
            field_type = field_info.get("type")
            field_required = field_info.get("required", False)
            field = Field(
                ...,
                description=field_description,
                alias=field_serialization_alias,
                serialization_alias=field_serialization_alias,
                min_length=1 if field_type == "array" and field_required else None,
            )

            if field_type == "object":
                python_type = self._schema_to_pydantic_model(
                    field_info.get("properties", {}) or {},
                    model_name=f"{model_name}{field_name.capitalize()}",
                    required=field_required,
                    is_root=False,
                )
            elif field_type == "array":
                python_type = List[  # type: ignore
                    self._items_schema_to_python_type(
                        field_info.get("items", {}) or {},
                        model_name=f"{model_name}Item",
                    )
                ]
            elif field_type == "enum":
                python_type = self._get_type(field_type, required=True)(
                    field_info["variants"]
                )
            elif expression := field_info.get("expression"):
                python_type = self._get_type(field_type, required=False)
                field = Field(
                    default=None,
                    description=field_description,
                    serialization_alias=field_serialization_alias,
                )
                computed_fields[field_name] = expression
            else:
                python_type = self._get_type(field_type, required=field_required)

            fields[field_name] = (python_type, field)

        config: ConfigDict = {"extra": "forbid", "str_strip_whitespace": True}
        config.update(schema.get("__config__", {}))
        base_model = base_model_factory(
            config, computed_fields, self.evaluator, is_root
        )
        new_model = create_model(model_name, __base__=base_model, **fields)

        if not required:
            new_model = Optional[new_model]

        return new_model

    def _get_type(self, field: SchemaFieldType, required: bool | None) -> Type[Any]:
        field_type = self.field_types.get(field)
        if not field_type:
            raise ValueError(f"Unsupported field type: {field}")
        if not required:
            field_type = Optional[field_type]
        return field_type


def base_model_factory(
    config: ConfigDict,
    computed_fields: dict[str, str],
    evaluator: ExpressionEvaluator,
    is_root: bool = True,
) -> Type[BaseModel]:
    class PreValidatedBaseModel(BaseModel):
        model_config: ConfigDict = config

        # noinspection PyNestedDecorators
        @model_validator(mode="before")
        @classmethod
        def pre_validate(cls, values: Any) -> Any:
            def trim_and_nullify(value: Any) -> Any:
                if isinstance(value, str):
                    value = value.strip()
                    if not value:
                        return None
                if isinstance(value, list):
                    return [trim_and_nullify(v) for v in value]
                if isinstance(value, dict):
                    return {k.strip(): trim_and_nullify(v) for k, v in value.items()}
                return value

            return trim_and_nullify(values)

        @model_validator(mode="after")
        def post_validate(self) -> Self:
            for field, expression in computed_fields.items():
                res = evaluator.evaluate(expression, self)
                setattr(self, field, res)

            # Only check for empty fields at the root level
            if is_root and _all_fields_empty(self.model_dump()):
                raise SchemaValidationError(
                    message=f"All fields are null or empty. data={self.model_dump()}",
                )

            return self

    return PreValidatedBaseModel


def _all_fields_empty(data: dict[str, Any]) -> bool:
    """
    Check if all fields in the base object are either None or empty recursively.
    This does not get called for individual fields in the base object.
    """

    def is_empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, dict):
            return all(is_empty(v) for v in value.values())
        if isinstance(value, list):
            return all(is_empty(v) for v in value)
        if isinstance(value, str):
            return not value.strip()
        return False

    return all(is_empty(value) for value in data.values())

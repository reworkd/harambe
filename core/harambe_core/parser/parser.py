from typing import Any, List, Optional, Type, Self

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    create_model,
    ConfigDict,
    model_validator,
)

from harambe_core.errors import SchemaValidationError
from harambe_core.parser.expression import ExpressionEvaluator
from harambe_core.parser.type_currency import ParserTypeCurrency
from harambe_core.parser.type_date import ParserTypeDate
from harambe_core.parser.type_email import ParserTypeEmail
from harambe_core.parser.type_enum import ParserTypeEnum
from harambe_core.parser.type_number import ParserTypeNumber
from harambe_core.parser.type_phone_number import ParserTypePhoneNumber
from harambe_core.parser.type_string import ParserTypeString
from harambe_core.parser.type_url import ParserTypeUrl
from harambe_core.types import Schema
from harambe_core.types import SchemaFieldType


class SchemaParser:
    """
    A schema parser that uses Pydantic models to validate data against a JSON schema
    """

    def __init__(
        self, schema: Schema, evaluator: ExpressionEvaluator | None = None
    ) -> None:
        self._pk_expression = schema.get("$pk", None)

        if "$schema" in schema:
            del schema["$schema"]
        if "$pk" in schema:
            del schema["$pk"]

        if evaluator is None:
            evaluator = ExpressionEvaluator()

        self.evaluator = evaluator
        self.schema = schema
        self.field_types: dict[SchemaFieldType, Any] = {}
        self.all_required_fields = self._get_all_required_fields(self.schema)

    def validate(self, data: dict[str, Any], base_url: str) -> dict[str, Any]:
        # Set these values here for convenience to avoid passing them around. A bit hacky
        self.field_types = self._get_field_types(base_url)
        model = self._schema_to_pydantic_model(self.schema)
        missing_fields = self._find_missing_required_fields(
            data, self.all_required_fields
        )

        if missing_fields:
            raise SchemaValidationError(
                message=f"Missing required fields: {', '.join(missing_fields)}, All required fields are: {', '.join(self.all_required_fields)}",
            )
        if self._all_fields_empty(data):
            raise SchemaValidationError(
                message="All fields are null or empty.",
            )
        try:
            res = model(**data).model_dump()
            if self._pk_expression:
                res["$pk"] = self.evaluator.evaluate(self._pk_expression, res)
            return res

        except ValidationError as validation_error:
            raise SchemaValidationError(message=str(validation_error))

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
            return self._get_type(item_type)(items_info["variants"])

        return self._get_type(item_type)

    def _schema_to_pydantic_model(
        self, schema: Schema, model_name: str = "DynamicModel"
    ) -> Type[BaseModel]:
        """
        Convert a JSON schema to a Pydantic model dynamically. All fields are optional
        """
        fields = {}
        computed_fields = {}

        for field_name, field_info in schema.items():
            if field_name == "__config__":
                continue

            field_description = field_info.get("description", None)
            field_type = field_info.get("type")
            field = Field(..., description=field_description)

            if field_type == "object":
                python_type = self._schema_to_pydantic_model(
                    field_info.get("properties", {}) or {},
                    model_name=f"{model_name}{field_name.capitalize()}",
                )
            elif field_type == "array":
                python_type = List[  # type: ignore
                    self._items_schema_to_python_type(
                        field_info.get("items", {}) or {},
                        model_name=f"{model_name}Item",
                    )
                ]
            elif field_type == "enum":
                python_type = self._get_type(field_type)(field_info["variants"])
            elif expression := field_info.get("expression"):
                python_type = self._get_type(field_type)
                field = Field(default=None, description=field_description)
                computed_fields[field_name] = expression
            else:
                python_type = Optional[self._get_type(field_type)]  # type: ignore

            fields[field_name] = (python_type, field)

        config: ConfigDict = {"extra": "forbid", "str_strip_whitespace": True}
        config.update(schema.get("__config__", {}))
        base_model = base_model_factory(config, computed_fields, self.evaluator)

        return create_model(model_name, __base__=base_model, **fields)

    def _get_all_required_fields(
        self, schema: Schema, parent_key: str = ""
    ) -> List[str]:
        """
        Recursively collect all required fields from the schema, including nested ones.
        """
        required_fields = []
        for field_name, field_info in schema.items():
            full_key = f"{parent_key}.{field_name}" if parent_key else field_name
            if field_info.get("required", False):
                required_fields.append(full_key)

            if field_info.get("type") == "object":
                nested_properties = field_info.get("properties", {})
                required_fields.extend(
                    self._get_all_required_fields(nested_properties, full_key)
                )
            elif field_info.get("type") == "array":
                item_info = field_info.get("items", {})
                if item_info.get("type") == "object":
                    nested_properties = item_info.get("properties", {})
                    required_fields.extend(
                        self._get_all_required_fields(nested_properties, full_key)
                    )

        return required_fields

    def _find_missing_required_fields(
        self, data: dict[str, Any], required_fields: List[str]
    ) -> List[str]:
        """
        Check the data against the list of required fields and find which are missing or None.
        """
        missing_fields = []

        def is_empty(value: Any) -> bool:
            return (
                value is None
                or (isinstance(value, str) and not value.strip())
                or (isinstance(value, (list, dict)) and not value)
            )

        def check_value(data: Any, field_path: str) -> None:
            keys = field_path.split(".")
            for key in keys[:-1]:
                if isinstance(data, dict):
                    data = data.get(key, None)
                elif isinstance(data, list):
                    data = [
                        item.get(key, None) if isinstance(item, dict) else None
                        for item in data
                    ]
                else:
                    return

            final_key = keys[-1]
            if isinstance(data, dict):
                if is_empty(data.get(final_key)):
                    missing_fields.append(field_path)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and is_empty(item.get(final_key)):
                        missing_fields.append(field_path)
            elif final_key and is_empty(data):
                missing_fields.append(field_path)

        for field in required_fields:
            check_value(data, field)

        return missing_fields

    def _get_type(self, field: SchemaFieldType) -> Type[Any]:
        field_type = self.field_types.get(field)
        if not field_type:
            raise ValueError(f"Unsupported field type: {field}")
        return field_type

    def _all_fields_empty(self, data: dict[str, Any]) -> bool:
        """
        Recursively check if all fields in the data are either None or empty.
        This includes handling nested dictionaries and lists.
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


def base_model_factory(
    config: ConfigDict, computed_fields: dict[str, str], evaluator: ExpressionEvaluator
) -> Type[BaseModel]:
    class PreValidatedBaseModel(BaseModel):
        model_config: ConfigDict = config

        # noinspection PyNestedDecorators
        @model_validator(mode="before")
        @classmethod
        def normalize_keys(cls, values: Any) -> Any:
            if isinstance(values, dict):
                values = {k.strip(): v for k, v in values.items()}
            return values

        # noinspection PyNestedDecorators
        @model_validator(mode="before")
        @classmethod
        def nullify_empty_strings(cls, values: Any) -> Any:
            def trim_and_nullify(value: Any) -> Any:
                if isinstance(value, str):
                    value = value.strip()
                    if not value:
                        return None
                if isinstance(value, list):
                    return [trim_and_nullify(v) for v in value]
                if isinstance(value, dict):
                    return {k: trim_and_nullify(v) for k, v in value.items()}
                return value

            if isinstance(values, dict):
                values = {k: trim_and_nullify(v) for k, v in values.items()}

            return values

        @model_validator(mode="after")
        def evaluate_computed_fields(self) -> Self:
            for field, expression in computed_fields.items():
                res = evaluator.evaluate(expression, self)
                setattr(self, field, res)
            return self

    return PreValidatedBaseModel

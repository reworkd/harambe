from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, Union, Dict

from pydantic import BaseModel, Extra, Field, NameEmail, ValidationError, create_model

from harambe.parser.type_currency import ParserTypeCurrency
from harambe.parser.type_date import ParserTypeDate
from harambe.parser.type_enum import ParserTypeEnum
from harambe.parser.type_number import ParserTypeNumber
from harambe.parser.type_phone_number import ParserTypePhoneNumber
from harambe.parser.type_url import ParserTypeUrl
from harambe.types import URL, Schema
from harambe.errors import SchemaValidationError

OBJECT_TYPE = "object"
LIST_TYPE = "array"


class SchemaParser(ABC):
    """
    Interface for schema parsers
    """

    @abstractmethod
    def validate(self, data: dict[str, Any], base_url: URL) -> Any:
        pass


class PydanticSchemaParser(SchemaParser):
    """
    A schema parser that uses Pydantic models to validate data against a JSON schema
    """

    model: Type[BaseModel]

    def __init__(self, schema: Schema):
        self.schema = schema
        self.field_types: dict[str, Any] = {}
        self.all_required_fields = self._get_all_required_fields(self.schema)

    def validate(self, data: dict[str, Any], base_url: URL) -> dict[str, Any]:
        # Set these values here for convenience to avoid passing them around. A bit hacky
        self.field_types = self._get_field_types(base_url)
        self.model = self._schema_to_pydantic_model(self.schema)
        cleaned_data = trim_keys_and_strip_values(data)
        missing_fields = self._find_missing_required_fields(
            cleaned_data, self.all_required_fields
        )
        if missing_fields:
            raise SchemaValidationError(
                data=cleaned_data,
                schema=self.schema,
                message=f"Missing required fields: {', '.join(missing_fields)}, All required fields are: {', '.join(self.all_required_fields)}",
            )
        if self._all_fields_empty(cleaned_data):
            raise SchemaValidationError(
                data=cleaned_data,
                schema=self.schema,
                message="All fields are null or empty.",
            )
        try:
            return self.model(**cleaned_data).model_dump()
        except ValidationError as validation_error:
            raise SchemaValidationError(
                data=cleaned_data, schema=self.schema, message=str(validation_error)
            )

    @staticmethod
    def _get_field_types(base_url: str) -> dict[str, Any]:
        return {
            "string": str,
            "str": str,
            "boolean": bool,
            "bool": bool,
            "integer": int,
            "int": int,
            "number": ParserTypeNumber,
            "float": ParserTypeNumber,
            "double": ParserTypeNumber,
            "currency": ParserTypeCurrency(),
            "email": NameEmail,
            "enum": ParserTypeEnum,
            LIST_TYPE: List,
            OBJECT_TYPE: dict[str, Any],
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

        if item_type == OBJECT_TYPE:
            python_type = self._schema_to_pydantic_model(
                items_info.get("properties", {}),
                model_name=f"{model_name}Object",
            )
        elif item_type == LIST_TYPE:
            # Lists can't be null
            python_type = List[  # type: ignore
                self._items_schema_to_python_type(
                    items_info.get("items", {}),
                    model_name=f"{model_name}Item",
                )
            ]
        elif item_type == "enum":
            # Every enum has its own unique variants
            python_type = self._get_type(item_type)(items_info["variants"])
        else:
            # Non complex types aren't optional when they're within a list
            python_type = self._get_type(item_type)

        return python_type

    def _schema_to_pydantic_model(
        self, schema: Schema, model_name: str = "DynamicModel"
    ) -> Type[BaseModel]:
        """
        Convert a JSON schema to a Pydantic model dynamically. All fields are optional
        """
        fields = {}

        for field_name, field_info in schema.items():
            field_description = field_info.get("description", None)
            field_type = field_info.get("type")

            if field_type == OBJECT_TYPE:
                python_type = self._schema_to_pydantic_model(
                    field_info.get("properties", {}) or {},
                    model_name=f"{model_name}{field_name.capitalize()}",
                )
            elif field_type == LIST_TYPE:
                # Lists can't be null
                python_type = List[  # type: ignore
                    self._items_schema_to_python_type(
                        field_info.get("items", {}) or {},
                        model_name=f"{model_name}Item",
                    )
                ]
            elif field_type == "enum":
                # Every enum has its own unique variants
                python_type = self._get_type(field_type)(field_info["variants"])
            else:
                # Non complex types should be optional
                python_type = Optional[self._get_type(field_type)]  # type: ignore

            fields[field_name] = (
                python_type,
                Field(..., description=field_description),
            )

        # Disallow additional fields
        config = {"extra": Extra.forbid}

        return create_model(model_name, __config__=config, **fields)  # type: ignore

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

            if field_info.get("type") == OBJECT_TYPE:
                nested_properties = field_info.get("properties", {})
                required_fields.extend(
                    self._get_all_required_fields(nested_properties, full_key)
                )
            elif field_info.get("type") == LIST_TYPE:
                item_info = field_info.get("items", {})
                if item_info.get("type") == OBJECT_TYPE:
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

    def _get_type(self, field: str) -> Type[Any]:
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


# TODO: Make this a root pre validator


def trim_keys_and_strip_values(
    data: Union[Dict[str, Any], Any],
) -> Union[Dict[str, Any], Any]:
    """
    Recursively trim dictionary keys and strip string values.
    This includes handling nested dictionaries and lists.
    Leaving nulls, numbers, empty lists, and empty dicts unchanged.
    """

    def process_value(value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        if isinstance(value, dict):
            return {k.strip(): process_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [process_value(v) for v in value]
        return value

    return process_value(data)

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, create_model, Extra, Field, NameEmail, ValidationError

from harambe.parser.type_date import ParserTypeDate
from harambe.parser.type_enum import ParserTypeEnum
from harambe.parser.type_phone_number import ParserTypePhoneNumber
from harambe.parser.type_url import ParserTypeUrl
from harambe.types import Schema, URL, ScrapeResult

OBJECT_TYPE = "object"
LIST_TYPE = "array"


class SchemaParser(ABC):
    """
    Interface for schema parsers
    """

    @abstractmethod
    def validate(self, data: Dict[str, Any], base_url: URL) -> None:
        pass


class SchemaValidationError(Exception):
    def __init__(self, schema: Schema, data: ScrapeResult, message: str):
        super().__init__(
            "Data {data} does not match schema {schema}. {message}".format(
                data=data, schema=schema, message=message
            )
        )


class PydanticSchemaParser(SchemaParser):
    """
    A schema parser that uses Pydantic models to validate data against a JSON schema
    """

    def __init__(self, schema: Schema):
        self.schema = schema
        self.model = None
        self.field_types = None

    def validate(self, data: Dict[str, Any], base_url: URL) -> Dict[str, Any]:
        # Set these values here for convenience to avoid passing them around. A bit hacky
        self.field_types = self._get_field_types(base_url)

        self.model = self._schema_to_pydantic_model(self.schema)

        try:
            return self.model(**data).dict()
        except ValidationError as validation_error:
            raise SchemaValidationError(
                data=data, schema=self.schema, message=validation_error
            )

    @staticmethod
    def _get_field_types(base_url: str) -> Dict[str, Type]:
        return {
            "string": str,
            "str": str,
            "boolean": bool,
            "bool": bool,
            "integer": int,
            "int": int,
            "number": float,
            "float": float,
            "double": float,
            "email": NameEmail,
            "enum": ParserTypeEnum,
            LIST_TYPE: List,
            OBJECT_TYPE: Dict[str, Any],
            "datetime": ParserTypeDate(),
            "phone_number": ParserTypePhoneNumber(),
            "url": ParserTypeUrl(base_url=base_url),
        }

    def _items_schema_to_python_type(
        self, items_info: Schema, model_name: str = "DynamicModelItem"
    ) -> Type:
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
            python_type = List[
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
                python_type = List[
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
                python_type = Optional[self._get_type(field_type)]

            fields[field_name] = (
                python_type,
                Field(..., description=field_description),
            )

        # Disallow additional fields
        config = {"extra": Extra.forbid}

        return create_model(model_name, __config__=config, **fields)

    def _get_type(self, field: str) -> Type[Any]:
        field_type = self.field_types.get(field)
        if not field_type:
            raise ValueError(f"Unsupported field type: {field}")
        return field_type

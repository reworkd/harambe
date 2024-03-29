from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional

from pydantic import BaseModel, create_model, Field, AnyUrl, Extra


class SchemaParser(ABC):
    """
    Interface for schema parsers
    """

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> None:
        pass


class PydanticSchemaParser(SchemaParser):
    """
    A schema parser that uses Pydantic models to validate data against a JSON schema
    """

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.model = _schema_to_pydantic_model(schema)

    def validate(self, data: Dict[str, Any]) -> None:
        self.model(**data)


def _schema_to_pydantic_model(
    schema: Dict[str, Any], model_name: str = "DynamicModel"
) -> Type[BaseModel]:
    """
    Convert a JSON schema to a Pydantic model dynamically. All fields are optional
    """
    fields = {}

    for field_name, field_info in schema.items():
        field_description = field_info.get("description", None)
        field_type = field_info.get("type")

        if field_type == OBJECT_TYPE:
            python_type = _schema_to_pydantic_model(
                field_info.get("properties", {}),
                model_name=f"{model_name}{field_name.capitalize()}",
            )
        else:
            # Non complex types should be optional
            python_type = Optional[get_type(field_type)]

        fields[field_name] = (python_type, Field(..., description=field_description))

    # Disallow additional fields
    config = {"extra": Extra.forbid}

    return create_model(model_name, __config__=config, **fields)


def get_type(field: str) -> Type:
    field_type = BASIC_FIELD_TYPE_MAPPING.get(field)
    if not field_type:
        raise ValueError(f"Unsupported field type: {field}")
    return field_type


OBJECT_TYPE = "object"
LIST_TYPE = "array"
COMPLEX_TYPES = [OBJECT_TYPE, LIST_TYPE]
BASIC_FIELD_TYPE_MAPPING = {
    "string": str,
    "str": str,
    "boolean": bool,
    "bool": bool,
    "integer": int,
    "int": int,
    "number": float,
    "float": float,
    "double": float,
    # TODO: Add support for date and datetime types
    # TODO: The URL type should have a custom validator to handle relative URLs
    "url": AnyUrl,
}

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional

from pydantic import BaseModel, create_model, Field, AnyUrl, Extra


class SchemaParser(ABC):
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> None:
        pass


FIELD_TYPE_MAPPING = {
    "string": str,
    "str": str,

    "boolean": bool,
    "bool": bool,

    "integer": int,
    "int": int,
    "number": float,
    "float": float,
    "double": float,

    "url": AnyUrl,
}


def _schema_to_pydantic_model(schema: Dict[str, Any]) -> Type[BaseModel]:
    """
    Convert a JSON schema to a Pydantic model dynamically. All fields are optional
    """
    fields = {}

    for field_name, field_info in schema.items():
        field_description = field_info.get('description', None)
        field_type = field_info['type']
        python_type = FIELD_TYPE_MAPPING.get(field_type)
        optional_python_type = Optional[python_type]

        if python_type is None:
            raise ValueError(f"Unsupported field type: {field_type}")

        fields[field_name] = (optional_python_type, Field(..., description=field_description))

    # Disallow additional fields
    config = {'extra': Extra.forbid}

    dynamic_model = create_model('DynamicModel', __config__=config, **fields)
    return dynamic_model


class PydanticSchemaParser(SchemaParser):
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.model = _schema_to_pydantic_model(schema)

    def validate(self, data: Dict[str, Any]) -> None:
        self.model(**data)

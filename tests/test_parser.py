from typing import Any

import pytest
from pydantic import ValidationError

from harambe.parser.parser import PydanticSchemaParser

document_schema = {
    "title": {"type": "string", "description": "The name of the document"},
    "document_url": {"type": "string", "actions": {"download": True}, "description": "A link to the document"}
}

contact_schema = {
    "name": {"type": "object", "properties": {
        "first_name": {"type": "string", "description": "The first name of the contact"},
        "last_name": {"type": "string", "description": "The last name of the contact"},
    }},
    "address": {"type": "object", "properties": {
        "street": {"type": "string", "description": "The street of the address"},
        "city": {"type": "string", "description": "The city of the address"},
        "zip": {"type": "int", "description": "The zip code of the address"},
    }}
}


@pytest.mark.parametrize("schema, data", [
    (document_schema, {"title": "Document One", "document_url": "http://example.com/doc1"}),
    (document_schema, {"title": "An interesting document title", "document_url": "https://example.com/doc2"}),
    (document_schema, {"title": "", "document_url": ""}),
    (document_schema, {"title": None, "document_url": None}),
    (contact_schema, {
        "name": {"first_name": "Jane", "last_name": "Doe"},
        "address": {"street": "456 Elm St", "city": "Othertown", "zip": 67890}
    }),
    (contact_schema, {
        "name": {"first_name": None, "last_name": None},
        "address": {"street": None, "city": None, "zip": None}
    }),
])
def test_pydantic_schema_validator_success(schema: dict[str, Any], data: dict[str, Any]) -> None:
    validator = PydanticSchemaParser(schema)
    validator.validate(data)


@pytest.mark.parametrize("schema, data", [
    (document_schema, {
        "title": "Document One", "document_url": "http://example.com/doc1", "items": {"title": "Extra field"}
    }),  # Extra field
    (document_schema, {"title": "Document Three", "document_url": 123}),  # Invalid URL type
    (document_schema, {"title": 456, "document_url": "http://example.com/doc4"}),  # Invalid title type
    (document_schema, {"document_url": "http://example.com/doc5"}),  # Missing title
    (document_schema, {}),  # Missing everything
    (contact_schema, {
        "name": {"first_name": None, "last_name": "Doe"},
        "address": None
    }),  # None sub-fields 
])
def test_pydantic_schema_validator_error(schema: dict[str, Any], data: dict[str, Any]) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(ValidationError):
        validator.validate(data)

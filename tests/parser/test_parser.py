from typing import Any

import pytest

from harambe.parser.parser import PydanticSchemaParser, SchemaValidationError
import tests.parser.schemas as schemas
from harambe.types import Schema


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": "Document One", "document_url": "http://example.com/doc1"},
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "An interesting document title",
                "document_url": "https://example.com/doc2",
            },
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": "", "document_url": ""},
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": None, "document_url": None},
        ),
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": "Jane", "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
            },
        ),
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": None},
                "address": {"street": None, "city": None, "zip": None},
            },
        ),
        (
            # Schema
            schemas.documents_schema,
            # Data
            {"documents": []},
        ),
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": [
                    {
                        "title": "Document One",
                        "document_url": "http://example.com/doc1",
                    },
                ]
            },
        ),
        (
            # Schema
            schemas.list_of_strings_schema,
            # Data
            {"tags": ["python", "pydantic", "typing"]},
        ),
        (
            # Schema
            schemas.list_of_objects_schema,
            # Data
            {
                "users": [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"},
                ]
            },
        ),
        (
            # Schema
            schemas.object_with_list_schema,
            # Data
            {"team": {"name": "Developers", "members": ["Alice", "Bob"]}},
        ),
        (
            # Schema
            schemas.list_of_lists_schema,
            # Data
            {"matrix": [[1, 2], [3, 4]]},
        ),
        (
            # Schema
            schemas.nested_lists_and_objects_schema,
            # Data
            {
                "departments": [
                    {
                        "name": "Engineering",
                        "teams": [
                            {"team_name": "Backend", "members": ["Alice", "Bob"]}
                        ],
                    }
                ]
            },
        ),
    ],
)
def test_pydantic_schema_validator_success(
    schema: Schema, data: dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    validator.validate(data)


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "Document One",
                "document_url": "http://example.com/doc1",
                "items": {  # ❌ Extra field
                    "title": "Extra field"
                },
            },
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "Document Three",
                "document_url": 123,  # ❌ Invalid URL type
            },
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": 456,  # ❌ Invalid title type
                "document_url": "http://example.com/doc4",
            },
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                # ❌ Missing title
                "document_url": "http://example.com/doc5"
            },
        ),
        (
            # Schema
            schemas.document_schema,
            # Data
            {},  # ❌ Missing everything
        ),
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": None,  # ❌ No sub-fields
            },
        ),
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": None  # ❌ Null list
            },
        ),
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": [
                    None  # ❌ Null item in list
                ]
            },
        ),
        (
            # Schema
            schemas.list_of_strings_schema,
            # Data
            {
                "tags": [
                    None,  # ❌ None in list of strings
                    "pydantic",
                    "typing",
                ]
            },
        ),
        (
            # Schema
            schemas.list_of_objects_schema,
            # Data
            {
                "users": [
                    {
                        "name": "Alice",
                        "email": 12345,  # ❌ Invalid email type
                    }
                ]
            },
        ),
        (
            # Schema
            schemas.object_with_list_schema,
            # Data
            {
                "team": {
                    "name": "Developers",
                    "members": [None],  # ❌ None in sub-list
                }
            },
        ),
        (
            # Schema
            schemas.list_of_lists_schema,
            # Data
            {
                "matrix": [
                    [1, "a"],  # ❌ Invalid type in nested list
                    [3, 4],
                ]
            },
        ),
        (
            # Schema
            schemas.nested_lists_and_objects_schema,
            # Data
            {
                "departments": [
                    {
                        "name": "Engineering",
                        "teams": [
                            {
                                "team_name": "Backend",
                                "members": [
                                    "Alice",
                                    None,  # ❌ None in nested object list
                                ],
                            }
                        ],
                    }
                ]
            },
        ),
    ],
)
def test_pydantic_schema_validator_error(schema: Schema, data: dict[str, Any]) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data)


@pytest.mark.parametrize(
    "schema",
    [
        schemas.non_existing_type_schema,
    ],
)
def test_pydantic_schema_initialization_error(schema: Schema) -> None:
    with pytest.raises(ValueError):
        PydanticSchemaParser(schema)

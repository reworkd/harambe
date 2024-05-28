from typing import Any

import pytest

from harambe.parser.parser import PydanticSchemaParser, SchemaValidationError
import tests.parser.schemas as schemas
from harambe.types import Schema


@pytest.mark.parametrize(
    "schema, data",
    [
        # 0
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": "Document One", "document_url": "http://example.com/doc1"},
        ),
        # 1
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "An interesting document title",
                "document_url": "https://example.com/doc2",
            },
        ),
        # 2
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": "", "document_url": ""},
        ),
        # 3
        (
            # Schema
            schemas.document_schema,
            # Data
            {"title": None, "document_url": None},
        ),
        # 4
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": "Jane", "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"type": "home", "number": "+1 (415) 555-1234"}],
            },
        ),
        # 5
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": None},
                "address": {"street": None, "city": None, "zip": None},
                "phone_numbers": [{"type": "mobile", "number": "+1 (628) 555-3456"}],
            },
        ),
        # 6
        (
            # Schema
            schemas.documents_schema,
            # Data
            {"documents": []},
        ),
        # 7
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
        # 8
        (
            # Schema
            schemas.list_of_strings_schema,
            # Data
            {"tags": ["python", "pydantic", "typing"]},
        ),
        # 9
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
        # 10
        (
            # Schema
            schemas.object_with_list_schema,
            # Data
            {"team": {"name": "Developers", "members": ["Alice", "Bob"]}},
        ),
        # 11
        (
            # Schema
            schemas.list_of_lists_schema,
            # Data
            {"matrix": [[1, 2], [3, 4]]},
        ),
        # 12
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
        # 13
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": [
                    {
                        "title": "Document One",
                        "document_url": "/doc1",
                    },
                ]
            },
        ),
    ],
)
def test_pydantic_schema_validator_success(
    schema: Schema, data: dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data",
    [
        # 0
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
        # 1
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "Document Three",
                "document_url": 123,  # ❌ Invalid URL type
            },
        ),
        # 2
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": 456,  # ❌ Invalid title type
                "document_url": "http://example.com/doc4",
            },
        ),
        # 3
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                # ❌ Missing title
                "document_url": "http://example.com/doc5"
            },
        ),
        # 4
        (
            # Schema
            schemas.document_schema,
            # Data
            {},  # ❌ Missing everything
        ),
        # 5
        (
            # Schema
            schemas.document_schema,
            # Data
            {
                "title": "Document Six",
                "document_url": "gopher://example.com/doc6",  # ❌ Bad URL scheme
            },
        ),
        # 6
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": None,  # ❌ No sub-fields
            },
        ),
        # 7
        (
            # Schema
            schemas.contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"number": 1234567890}],  # ❌ Bad phone number
            },
        ),
        # 8
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": None  # ❌ Null list
            },
        ),
        # 9
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
        # 10
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
        # 11
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
        # 12
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
        # 13
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
        # 14
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
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data",
    [
        # 0
        (
            # Schema
            schemas.documents_schema,
            # Data
            {
                "documents": [
                    {
                        "title": "Document Seven",
                        "document_url": "/doc7",  # ❌ Relative URL, with bad base_url specified
                    },
                ]
            },
        ),
    ],
)
def test_pydantic_schema_validator_bad_base_url_error(
    schema: Schema, data: dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="gemini://example.com")


@pytest.mark.parametrize(
    "schema",
    [
        schemas.non_existing_type_schema,
    ],
)
def test_pydantic_schema_validator_non_existing_type_error(schema: Schema) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(ValueError):
        validator.validate({}, base_url="gemini://example.com")

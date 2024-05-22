from typing import Any

import pytest
from pydantic import ValidationError

from harambe.parser.parser import PydanticSchemaParser
from tests.parser.schemas import document_schema, contact_schema
from harambe.types import Schema


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            # Schema
            document_schema,
            # Data
            {"title": "Document One", "document_url": "http://example.com/doc1"},
        ),
        (
            # Schema
            document_schema,
            # Data
            {
                "title": "An interesting document title",
                "document_url": "https://example.com/doc2",
            },
        ),
        (
            # Schema
            document_schema,
            # Data
            {"title": "", "document_url": ""},
        ),
        (
            # Schema
            document_schema,
            # Data
            {"title": None, "document_url": None},
        ),
        (
            # Schema
            contact_schema,
            # Data
            {
                "name": {"first_name": "Jane", "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
            },
        ),
        (
            # Schema
            contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": None},
                "address": {"street": None, "city": None, "zip": None},
            },
        ),
        # TODO: Support lists and nested objects
        # (documents_schema, {"documents": []}),
        #
        # (documents_schema, {
        #     "documents": [
        #         {"title": "Document One", "document_url": "http://example.com/doc1"},
        #     ]
        # }),
        #
        # (list_of_strings_schema, {"tags": ["python", "pydantic", "typing"]}),
        #
        # (list_of_objects_schema,
        #  {"users": [{"name": "Alice", "email": "alice@example.com"}, {"name": "Bob", "email": "bob@example.com"}]}),
        #
        # (object_with_list_schema, {"team": {"name": "Developers", "members": ["Alice", "Bob"]}}),
        #
        # (list_of_lists_schema, {"matrix": [[1, 2], [3, 4]]}),
        #
        # (nested_lists_and_objects_schema, {
        #     "departments": [
        #         {
        #             "name": "Engineering",
        #             "teams": [
        #                 {
        #                     "team_name": "Backend",
        #                     "members": ["Alice", "Bob"]
        #                 }
        #             ]
        #         }
        #     ]
        # }),
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
            document_schema,
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
            document_schema,
            # Data
            {
                "title": "Document Three",
                "document_url": 123,  # ❌ Invalid URL type
            },
        ),
        (
            # Schema
            document_schema,
            # Data
            {
                "title": 456,  # ❌ Invalid title type
                "document_url": "http://example.com/doc4",
            },
        ),
        (
            # Schema
            document_schema,
            # Data
            {
                # ❌ Missing title
                "document_url": "http://example.com/doc5"
            },
        ),
        (
            # Schema
            document_schema,
            # Data
            {},  # ❌ Missing everything
        ),
        (
            # Schema
            contact_schema,
            # Data
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": None,  # ❌ No sub-fields
            },
        ),
        # TODO: Support lists and nested objects
        # (documents_schema, {"documents": None}),  # Null list
        # (documents_schema, {"documents": [None]}),  # Null item in list
        # (list_of_strings_schema, {"tags": [None, "pydantic", "typing"]}),  # None in list of strings
        # (list_of_objects_schema, {"users": [{"name": "Alice", "email": 12345}]}),  # Invalid email type
        # (object_with_list_schema, {"team": {"name": "Developers", "members": [None]}}),  # None in sub-list
        # (list_of_lists_schema, {"matrix": [[1, "a"], [3, 4]]}),  # Invalid type in nested list
        # (nested_lists_and_objects_schema, {
        #     "departments": [
        #         {
        #             "name": "Engineering",
        #             "teams": [
        #                 {
        #                     "team_name": "Backend",
        #                     "members": ["Alice", None]  # None in nested object list
        #                 }
        #             ]
        #         }
        #     ]
        # }),
    ],
)
def test_pydantic_schema_validator_error(schema: Schema, data: dict[str, Any]) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(ValidationError):
        validator.validate(data)

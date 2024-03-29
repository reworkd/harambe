from typing import Any

import pytest
from pydantic import ValidationError

from harambe.parser.parser import PydanticSchemaParser
from tests.parser.schemas import document_schema, contact_schema


@pytest.mark.parametrize("schema, data", [
    (document_schema, {"title": "Document One", "document_url": "http://example.com/doc1"}),
    (document_schema, {"title": "An interesting document title", "document_url": "https://example.com/doc2"}),
    (document_schema, {"title": "", "document_url": ""}),
    (document_schema, {"title": None, "document_url": None}),
    (contact_schema, {
        "name": {"first_name": "Jane", "last_name": "Doe"},
        "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890}
    }),
    (contact_schema, {
        "name": {"first_name": None, "last_name": None},
        "address": {"street": None, "city": None, "zip": None}
    }),
    # TODO: Support lists and nested objects
    # (documents_schema, {"documents": []}),
    # (documents_schema, {
    #     "documents": [
    #         {"title": "Document One", "document_url": "http://example.com/doc1"},
    #     ]
    # }),
    # (list_of_strings_schema, {"tags": ["python", "pydantic", "typing"]}),
    # (list_of_objects_schema,
    #  {"users": [{"name": "Alice", "email": "alice@example.com"}, {"name": "Bob", "email": "bob@example.com"}]}),
    # (object_with_list_schema, {"team": {"name": "Developers", "members": ["Alice", "Bob"]}}),
    # (list_of_lists_schema, {"matrix": [[1, 2], [3, 4]]}),
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
])
def test_pydantic_schema_validator_error(schema: dict[str, Any], data: dict[str, Any]) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(ValidationError):
        validator.validate(data)

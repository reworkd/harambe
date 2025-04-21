from typing import Any

import pytest
from harambe_core.errors import SchemaValidationError
from harambe_core.parser.parser import SchemaParser
from harambe_core.types import Schema

from test.parser.mock_schemas.load_schema import load_schema


@pytest.mark.parametrize("data", [None, {}, ""])
def test_no_data(data) -> None:
    schema = load_schema("document")
    validator = SchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            {"price": {"type": "number", "description": "The price of the product"}},
            {"price": "1,515.99"},
        ),
        (
            load_schema("document"),
            {"title": "Document One", "document_url": "http://example.com/doc1"},
        ),
        (
            load_schema("document"),
            {
                "title": "An interesting document title",
                "document_url": "https://example.com/doc2",
            },
        ),
        (
            load_schema("contact"),
            {
                "name": {"first_name": "Jane", "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"type": "home", "number": "+1 (415) 555-1234"}],
            },
        ),
        (
            load_schema("contact"),
            {
                "name": {"first_name": "Adam", "last_name": None},
                "address": {"street": None, "city": None, "zip": "9104"},
                "phone_numbers": [{"type": "mobile", "number": "+1 (628) 555-3456"}],
            },
        ),
        (
            load_schema("documents"),
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
            load_schema("list_of_strings"),
            {"tags": ["python", "pydantic", "typing"], "other_field": ""},
        ),
        (
            load_schema("list_of_objects"),
            {
                "users": [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"},
                ],
                "other_field": "",
            },
        ),
        (
            load_schema("object_with_list"),
            {"team": {"name": "Developers", "members": ["Alice", "Bob"]}},
        ),
        (
            load_schema("list_of_lists"),
            {"matrix": [[1, 2], [3, 4]]},
        ),
        (
            load_schema("nested_lists_and_objects"),
            {
                " departments\n  \n\t": [  # ✅ handles all kinds of whitespace
                    {
                        "name ": "\u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 Engineering",
                        "teams\r": [
                            {" team_name \n  ": "Backend", "members": ["Alice", "Bob"]}
                        ],
                    }
                ]
            },
        ),
        (
            load_schema("documents"),
            {
                "documents": [
                    {
                        "title": "Document One",
                        "document_url": "/doc1",
                    },
                ]
            },
        ),
        (
            load_schema("documents"),
            {
                "documents ": [
                    {
                        " title  ": "Document One",
                        " document_url ": "/doc1",  # ✅ handles extra spaces
                    },
                ]
            },
        ),
        (
            load_schema("enums"),
            {"season": "spring"},
        ),
        (
            load_schema("enums"),
            {"season": "FALL \n"},
        ),
        (
            load_schema(
                "object_with_list_of_objects"
            ),  # ✅ parse object because list of strings has valid data
            {"list": [{"a": None, "b": ["Some imp data"], "c": {"d": "", "e": ""}}]},
        ),
        (
            load_schema(
                "object_with_list_of_objects"
            ),  # ✅ parse object because string has valid data
            {"list": [{"a": "Some imp data", "b": [], "c": {"d": "", "e": ""}}]},
        ),
        (
            load_schema(
                "object_with_list_of_objects"
            ),  # ✅ parse object because child object has valid data
            {"list": [{"a": None, "b": [], "c": {"d": "", "e": "Some imp data"}}]},
        ),
    ],
)
def test_pydantic_schema_validator_success(
    schema: Schema, data: dict[str, Any]
) -> None:
    validator = SchemaParser(schema)
    validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data, expected_data",
    [
        (
            {"url": {"type": "url"}},
            {"url": "s3://bucket-name/file-name.pdf"},
            {"url": "s3://bucket-name/file-name.pdf"},
        ),
        (
            {"url": {"type": "url"}},
            {"url": "/test"},
            {"url": "http://example.com/test"},
        ),
        (
            {"url": {"type": "url"}},
            {"url": "http://example.com/one two three"},
            {"url": "http://example.com/one%20two%20three"},
        ),
        (
            load_schema("documents"),
            {
                "documents": [
                    {
                        "title": "Document",
                        "document_url": "/doc1",
                    },
                ]
            },
            {
                "documents": [
                    {
                        "title": "Document",
                        "document_url": "http://example.com/doc1",
                    },
                ]
            },
        ),
        (
            load_schema("documents"),
            {
                "documents": [
                    {
                        "title": "Document",
                        "document_url": "https://www.test.com/FileDownload.aspx?file=6100061149/Protection Form .docx",
                    },
                ],
            },
            {
                "documents": [
                    {
                        "title": "Document",
                        "document_url": "https://www.test.com/FileDownload.aspx?file=6100061149/Protection%20Form%20.docx",
                    },
                ],
            },
        ),
        (
            {"test": {"type": "string"}, "phone_number": {"type": "phone_number"}},
            {"test": "Test", "phone_number": ""},
            {"test": "Test", "phone_number": None},
        ),
    ],
)
def test_pydantic_schema_data_update(
    schema: dict[str, Any], data: dict[str, Any], expected_data: dict[str, Any]
) -> None:
    validator = SchemaParser(schema)
    updated_data = validator.validate(data, base_url="http://example.com")
    assert updated_data == expected_data


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            load_schema("document"),
            {
                "title": "Document Three",
                "document_url": 123,
                "test": "Extra field",  # ❌ Extra field
            },
        ),
        (
            load_schema("document"),
            {
                "title": "Document One",
                "document_url": "http://example.com/doc1",
                "items": {"title": "Extra field"},  # ❌ Extra complex field
            },
        ),
        (
            load_schema("document"),
            {
                "title": "Document Three",
                "document_url": 123,  # ❌ Invalid URL type
            },
        ),
        (
            load_schema("document"),
            {
                "title": 456,  # ❌ Invalid title type
                "document_url": "http://example.com/doc4",
            },
        ),
        (
            load_schema("document"),
            {
                # ❌ Missing title
                "document_url": "http://example.com/doc5"
            },
        ),
        (
            load_schema("document"),
            {},  # ❌ Missing everything
        ),
        (
            load_schema("document"),
            {
                "title": "Document Six",
                "document_url": "gopher://example.com/doc6",  # ❌ Bad URL scheme
            },
        ),
        (
            load_schema("contact"),
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": None,  # ❌ No sub-fields
            },
        ),
        (
            load_schema("contact"),
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"number": 1234567890}],  # ❌ Bad phone number
            },
        ),
        (
            load_schema("documents"),
            {"documents": None},  # ❌ Null list
        ),
        (
            load_schema("documents"),
            {
                # ❌ Invalid type in list
                "documents": [
                    {
                        "title": "Document Seven",
                        "document_url": 1234,  # ❌ Invalid URL type
                    },
                ]
            },
        ),
        (
            load_schema("documents"),
            {
                "documents": [
                    {
                        "title": "Document Seven",
                        "document_url": "www.test.com",
                        "extra": "Extra field",  # ❌ Extra field in list
                    },
                ]
            },
        ),
        (
            load_schema("documents"),
            {"documents": [None]},  # ❌ Null item in list
        ),
        (
            load_schema("list_of_strings"),
            {
                "tags": [
                    None,  # ❌ None in list of strings
                    "pydantic",
                    "typing",
                ]
            },
        ),
        (
            load_schema("list_of_objects"),
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
            load_schema("object_with_list"),
            {
                "team": {
                    "name": "Developers",
                    "members": [None],  # ❌ None in sub-list
                }
            },
        ),
        (
            load_schema("list_of_lists"),
            {
                "matrix": [
                    [1, "a"],  # ❌ Invalid type in nested list
                    [3, 4],
                ]
            },
        ),
        (
            load_schema("nested_lists_and_objects"),
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
        (
            load_schema("enums"),
            {
                "season": "autumn"  # ❌ Value that doesn't match any of the enum variants
            },
        ),
        (
            load_schema("document"),
            {
                "title": None,
                "document_url": None,  # ❌ Do not allow objects with all null values
            },
        ),
        (
            load_schema("documents"),
            {"documents": []},  # ❌ Do not allow objects with all null arrays
        ),
        (
            load_schema("document"),
            {
                "title": "",  # ❌ Do not allow objects with all empty strings
                "document_url": "",
            },
        ),
        (
            load_schema("document"),
            {
                "title": "",  # ❌ Do not allow objects with all empty strings
                "document_url": "",
            },
        ),
        (
            load_schema("documents"),
            {
                "departments": [
                    {"name": "", "teams": [{"team_name": None, "members": []}]}
                ]
            },
        ),
        (
            load_schema("object_with_list_of_objects"),
            {"list": [{"a": None, "b": [], "c": {"d": "", "e": ""}}]},
        ),
        # ( #TODO: Fix this! This should error
        #     load_schema("object_with_list_of_objects"),
        #     {
        #         "list": [
        #             {"a": None, "b": [], "c": {"d": "", "e": ""}},
        #             {"a": "Hellooo", "b": [], "c": {"d": "", "e": ""}},
        #         ]
        #     },
        # ),
    ],
)
def test_pydantic_schema_validator_error(schema: Schema, data: dict[str, Any]) -> None:
    validator = SchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


def test_pydantic_schema_validator_bad_base_url_error() -> None:
    schema = load_schema("documents")
    data = {
        "documents": [
            {
                "title": "Document Seven",
                "document_url": "/doc7",
            },
        ]
    }

    validator = SchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="gemini://example.com")


def test_pydantic_schema_validator_non_existing_type_error() -> None:
    schema = {
        "title": {
            "type": "this_type_does_not_exist",
            "description": "Purely to cause error in the test",
        }
    }

    validator = SchemaParser(schema)
    with pytest.raises(ValueError):
        validator.validate({}, base_url="gemini://example.com")


def test_stripping_keeps_order() -> None:
    schema = {
        "full_name": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "fax_number": {"type": "string"},
        "phone_number": {"type": "string"},
        "email": {"type": "string"},
    }
    data = {
        "full_name": "John Doe",
        "first_name": " John",
        "last_name": "Doe",
        "fax_number": "+1 (800) 555-1234",
        "phone_number": "  +1 (800) 555-1234  ",
        "email": "",
    }
    expected = {
        "full_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "fax_number": "+1 (800) 555-1234",
        "phone_number": "+1 (800) 555-1234",
        "email": None,
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    for i in range(len(data)):
        assert list(output_data.keys())[i] == list(expected.keys())[i]
        assert list(output_data.values())[i] == list(expected.values())[i]


def test_allow_extra() -> None:
    schema = {
        "__config__": {"extra": "allow"},
        "first_name": {"type": "string"},
    }

    data = {
        "first_name": "Adam",
        "last_name": "Poop my pants",
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    assert output_data == data


def test_allow_extra_nested() -> None:
    schema = {
        "first_name": {"type": "string"},
        "address": {
            "type": "object",
            "properties": {
                "__config__": {"extra": "allow"},
                "street": {"type": "string"},
                "city": {"type": "string"},
            },
        },
        "phone_numbers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "__config__": {"extra": "allow"},
                    "type": {"type": "string"},
                    "number": {"type": "string"},
                },
            },
        },
    }

    data = {
        "first_name": "Adam",
        "address": {
            "street": "123 Elm St",
            "city": "Springfield",
            "zip": 12345,
        },
        "phone_numbers": [
            {"type": "home", "number": "+1 (800) 555-1234", "extra": "field"},
        ],
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    assert output_data == data


def test_config_ignore_extra_fields() -> None:
    schema = {
        "__config__": {"extra": "ignore"},
        "first_name": {"type": "string"},
    }

    data = {
        "first_name": "Adam",
        "last_name": "Poop my pants",
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    assert output_data == {"first_name": "Adam"}


def test_config_allow_extra_fields() -> None:
    schema = {
        "__config__": {"extra": "allow"},
        "first_name": {"type": "string"},
    }

    data = {
        "first_name": "Adam",
        "last_name": "Poop my pants",
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    assert output_data == data


def test_dump_email() -> None:
    schema = {
        "email": {"type": "email"},
    }

    data = {"email": "adam.watkins@gmail.com"}

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data == data
    assert isinstance(output_data["email"], str)

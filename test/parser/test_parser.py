from typing import Any

import pytest

import test.parser.schemas as schemas
from harambe.parser.parser import PydanticSchemaParser, SchemaValidationError
from harambe.types import Schema


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            {"price": {"type": "number", "description": "The price of the product"}},
            {"price": "1,515.99"},
        ),
        (
            schemas.document_schema,
            {"title": "Document One", "document_url": "http://example.com/doc1"},
        ),
        (
            schemas.document_schema,
            {
                "title": "An interesting document title",
                "document_url": "https://example.com/doc2",
            },
        ),
        (
            schemas.contact_schema,
            {
                "name": {"first_name": "Jane", "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"type": "home", "number": "+1 (415) 555-1234"}],
            },
        ),
        (
            schemas.contact_schema,
            {
                "name": {"first_name": None, "last_name": None},
                "address": {"street": None, "city": None, "zip": None},
                "phone_numbers": [{"type": "mobile", "number": "+1 (628) 555-3456"}],
            },
        ),
        (
            schemas.documents_schema,
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
            schemas.list_of_strings_schema,
            {"tags": ["python", "pydantic", "typing"]},
        ),
        (
            schemas.list_of_objects_schema,
            {
                "users": [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"},
                ]
            },
        ),
        (
            schemas.object_with_list_schema,
            {"team": {"name": "Developers", "members": ["Alice", "Bob"]}},
        ),
        (
            schemas.list_of_lists_schema,
            {"matrix": [[1, 2], [3, 4]]},
        ),
        (
            schemas.nested_lists_and_objects_schema,
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
            schemas.documents_schema,
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
            schemas.documents_schema,
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
            schemas.enums_schema,
            {"season": "spring"},
        ),
    ],
)
def test_pydantic_schema_validator_success(
    schema: Schema, data: dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
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
            schemas.documents_schema,
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
            schemas.documents_schema,
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
    ],
)
def test_pydantic_schema_data_update(
    schema: dict[str, Any], data: dict[str, Any], expected_data: dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    updated_data = validator.validate(data, base_url="http://example.com")
    assert updated_data == expected_data


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            schemas.document_schema,
            {
                "title": "Document Three",
                "document_url": 123,
                "test": "Extra field",  # ❌ Extra field
            },
        ),
        (
            schemas.document_schema,
            {
                "title": "Document One",
                "document_url": "http://example.com/doc1",
                "items": {  # ❌ Extra complex field
                    "title": "Extra field"
                },
            },
        ),
        (
            schemas.document_schema,
            {
                "title": "Document Three",
                "document_url": 123,  # ❌ Invalid URL type
            },
        ),
        (
            schemas.document_schema,
            {
                "title": 456,  # ❌ Invalid title type
                "document_url": "http://example.com/doc4",
            },
        ),
        (
            schemas.document_schema,
            {
                # ❌ Missing title
                "document_url": "http://example.com/doc5"
            },
        ),
        (
            schemas.document_schema,
            {},  # ❌ Missing everything
        ),
        (
            schemas.document_schema,
            {
                "title": "Document Six",
                "document_url": "gopher://example.com/doc6",  # ❌ Bad URL scheme
            },
        ),
        (
            schemas.contact_schema,
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": None,  # ❌ No sub-fields
            },
        ),
        (
            schemas.contact_schema,
            {
                "name": {"first_name": None, "last_name": "Doe"},
                "address": {"street": "456 Elm St", "city": "Other town", "zip": 67890},
                "phone_numbers": [{"number": 1234567890}],  # ❌ Bad phone number
            },
        ),
        (
            schemas.documents_schema,
            {
                "documents": None  # ❌ Null list
            },
        ),
        (
            schemas.documents_schema,
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
            schemas.documents_schema,
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
            schemas.documents_schema,
            {
                "documents": [
                    None  # ❌ Null item in list
                ]
            },
        ),
        (
            schemas.list_of_strings_schema,
            {
                "tags": [
                    None,  # ❌ None in list of strings
                    "pydantic",
                    "typing",
                ]
            },
        ),
        (
            schemas.list_of_objects_schema,
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
            schemas.object_with_list_schema,
            {
                "team": {
                    "name": "Developers",
                    "members": [None],  # ❌ None in sub-list
                }
            },
        ),
        (
            schemas.list_of_lists_schema,
            {
                "matrix": [
                    [1, "a"],  # ❌ Invalid type in nested list
                    [3, 4],
                ]
            },
        ),
        (
            schemas.nested_lists_and_objects_schema,
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
            schemas.enums_schema,
            {
                "season": "autumn"  # ❌ Value that doesn't match any of the enum variants
            },
        ),
        (
            schemas.document_schema,
            {
                "title": None,
                "document_url": None,  # ❌ Do not allow objects with all null values
            },
        ),
        (
            schemas.documents_schema,
            {
                "documents": []  # ❌ Do not allow objects with all null arrays
            },
        ),
        (
            schemas.document_schema,
            {
                "title": "",  # ❌ Do not allow objects with all empty strings
                "document_url": "",
            },
        ),
        (
            schemas.document_schema,
            {
                "title": "",  # ❌ Do not allow objects with all empty strings
                "document_url": "",
            },
        ),
        (
            schemas.nested_lists_and_objects_schema,
            {
                "departments": [
                    {"name": "", "teams": [{"team_name": None, "members": []}]}
                ]
            },
        ),
        (
            schemas.object_with_list_of_objects_schema,
            {"list": [{"members": {"a": None, "b": [], "c": {"d": "", "e": ""}}}]},
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
        (
            schemas.documents_schema,
            {
                "documents": [
                    {
                        "title": "Document Seven",
                        "document_url": "/doc7",
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

    validator = PydanticSchemaParser(schema)
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

    validator = PydanticSchemaParser(schema)
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

    validator = PydanticSchemaParser(schema)
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

    validator = PydanticSchemaParser(schema)
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

    validator = PydanticSchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")

    assert output_data == data

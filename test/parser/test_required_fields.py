from typing import Any, Dict
import pytest
import test.parser.schema_with_required_fields as schemas
from harambe.parser.parser import (
    PydanticSchemaParser,
    MissingRequiredFieldsError,
)


@pytest.mark.parametrize(
    "schema, data, expected_error, missing_fields",
    [
        (
            schemas.document_schema,
            {
                "title": None,  # required
                "document_url": None,  # required
            },
            MissingRequiredFieldsError,
            ["title", "document_url"],
        ),
        (
            schemas.documents_schema,
            {
                "documents": [
                    {
                        "title": "",  # required
                        "document_url": "",  # required
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["documents.title", "documents.document_url"],
        ),
        (
            schemas.contact_schema,
            {
                "name": {
                    "first_name": None,  # required
                    "last_name": "test",
                },
                "address": {
                    "street": "test",
                    "city": None,  # required
                    "zip": "test",
                },
                "phone_numbers": [
                    {
                        "type": "test",
                        "number": "test",
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["name.first_name", "address.city"],
        ),
        (
            schemas.list_of_strings_schema,
            {
                "tags": [],  # required
            },
            MissingRequiredFieldsError,
            ["tags"],
        ),
        (
            schemas.list_of_objects_schema,
            {
                "users": [
                    {
                        "name": None,  # required
                        "email": "test@test.com",
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["users.name"],
        ),
        (
            schemas.object_with_list_schema,
            {
                "team": {
                    "name": None,  # required
                    "members": ["test"],
                },
            },
            MissingRequiredFieldsError,
            ["team.name"],
        ),
        (
            schemas.object_with_list_of_objects_schema,
            {
                "list": [
                    {
                        "a": "test",  # required
                        "b": ["test"],
                        "c": {
                            "d": None,  # required
                            "e": "test",
                        },
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["list.c.d"],
        ),
        # TODO: use pydantic to validate and throw MissingRequiredFieldsError
        # (
        #     schemas.list_of_lists_schema,
        #     {
        #         "matrix": [[]],  # required
        #     },
        #     MissingRequiredFieldsError,
        #     ["matrix"],
        # ),
        (
            schemas.nested_lists_and_objects_schema,
            {
                "departments": [
                    {
                        "name": "",  # required
                        "teams": [
                            {
                                "team_name": "test",
                                "members": [],  # required
                            }
                        ],
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["departments.name", "departments.teams.members"],
        ),
        (
            schemas.datetime_schema,
            {
                "event": {
                    "name": None,  # required
                    "date": "05/29/2024 02:00:00 PM",
                },
            },
            MissingRequiredFieldsError,
            ["event.name"],
        ),
        (
            schemas.phone_number_schema,
            {
                "contact": {
                    "name": None,  # required
                    "phone": "11111111111",  # required
                },
            },
            MissingRequiredFieldsError,
            ["contact.name"],
        ),
        (
            schemas.url_schema,
            {
                "resource": {
                    "name": "",  # required
                    "link": "http://example.com",  # required
                },
            },
            MissingRequiredFieldsError,
            ["resource.name"],
        ),
        (
            schemas.object_with_nested_types_schema,
            {
                "profile": {
                    "user": None,  # required
                    "contact": "11111111111",
                    "event_date": "05/29/2024 02:00:00 PM",
                    "website": "http://example.com",
                },
            },
            MissingRequiredFieldsError,
            ["profile.user"],
        ),
        (
            schemas.list_with_nested_types_schema,
            {
                "events": [
                    {
                        "name": "",  # required
                        "dates": [],  # required
                        "contacts": [],  # required
                        "links": [],  # required
                    }
                ],
            },
            MissingRequiredFieldsError,
            ["events.name", "events.dates", "events.contacts", "events.links"],
        ),
        (
            {
                "name": {
                    "type": "string",
                    "required": True,
                    "description": "The name of the person",
                }
            },
            {},  # ❌ Missing the required "name" field
            MissingRequiredFieldsError,
            ["name"],
        ),
        (
            {
                "title": {
                    "type": "string",
                    "required": True,
                    "description": "The title of the document",
                },
                "document_url": {
                    "type": "url",
                    "required": True,
                    "description": "The URL of the document",
                },
            },
            {
                "document_url": "http://example.com/doc5"
            },  # ❌ Missing required "title" field
            MissingRequiredFieldsError,
            ["title"],
        ),
        (
            {
                "person": {
                    "type": "object",
                    "required": True,
                    "properties": {
                        "first_name": {"type": "string", "required": True},
                        "last_name": {"type": "string", "required": True},
                    },
                },
                "address": {
                    "type": "object",
                    "required": True,
                    "properties": {"street": {"type": "string", "required": True}},
                },
            },
            {
                "person": {"first_name": None},  # ❌ Missing "last_name" and "street"
                "address": {},  # Missing "street" in "address"
            },
            MissingRequiredFieldsError,
            ["person.first_name", "person.last_name", "address", "address.street"],
        ),
    ],
)
def test_pydantic_schema_validation_error_fail(
    schema: Dict[str, Any],
    data: Dict[str, Any],
    expected_error: Exception,
    missing_fields: list[str],
) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(expected_error) as exc_info:
        validator.validate(data, base_url="http://example.com")

    # Check if the raised error is MissingRequiredFieldsError and validate missing fields
    if expected_error == MissingRequiredFieldsError:
        assert exc_info.value.missing_fields == missing_fields


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            schemas.document_schema,
            {
                "title": "Document Title",  # required
                "document_url": "http://example.com/doc",  # required
            },
        ),
        (
            schemas.documents_schema,
            {
                "documents": [
                    {
                        "title": "Document Title",  # required
                        "document_url": "http://example.com/doc",  # required
                    }
                ],
            },
        ),
        (
            schemas.contact_schema,
            {
                "name": {
                    "first_name": "John",  # required
                    "last_name": None,
                },
                "address": {
                    "street": None,
                    "city": "Anytown",  # required
                    "zip": None,
                },
                "phone_numbers": [
                    {
                        "type": "home",
                        "number": "555-1234",
                    }
                ],
            },
        ),
        (
            schemas.list_of_strings_schema,
            {
                "tags": ["tag1", "tag2"],  # required
            },
        ),
        (
            schemas.list_of_objects_schema,
            {
                "users": [
                    {
                        "name": "John Doe",  # required
                        "email": None,
                    }
                ],
            },
        ),
        (
            schemas.object_with_list_schema,
            {
                "team": {
                    "name": "Dev Team",  # required
                    "members": ["Alice", "Bob"],  # required
                },
            },
        ),
        (
            schemas.object_with_list_of_objects_schema,
            {
                "list": [
                    {
                        "a": "Value A",  # required
                        "b": [],
                        "c": {
                            "d": "Value D",  # required
                            "e": None,
                        },
                    }
                ],
            },
        ),
        (
            schemas.list_of_lists_schema,
            {
                "matrix": [[1, 2], [3, 4]],  # required
            },
        ),
        (
            schemas.nested_lists_and_objects_schema,
            {
                "departments": [
                    {
                        "name": "Engineering",  # required
                        "teams": [
                            {
                                "team_name": None,
                                "members": ["Alice", "Bob"],  # required
                            }
                        ],
                    }
                ],
            },
        ),
        (
            schemas.datetime_schema,
            {
                "event": {
                    "name": "Launch",  # required
                    "date": "2024-09-24T12:00:00Z",
                },
            },
        ),
        (
            schemas.phone_number_schema,
            {
                "contact": {
                    "name": "Support",  # required
                    "phone": "+1234567890",  # required
                },
            },
        ),
        (
            schemas.url_schema,
            {
                "resource": {
                    "name": "Website",  # required
                    "link": "http://example.com",  # required
                },
            },
        ),
        (
            schemas.object_with_nested_types_schema,
            {
                "profile": {
                    "user": "johndoe",  # required
                    "contact": None,
                    "event_date": None,
                    "website": None,
                },
            },
        ),
        (
            schemas.list_with_nested_types_schema,
            {
                "events": [
                    {
                        "name": "Conference",  # required
                        "dates": ["2024-09-24T12:00:00Z"],  # required
                        "contacts": ["+1234567890"],  # required
                        "links": ["http://example.com"],  # required
                    }
                ],
            },
        ),
    ],
)
def test_pydantic_schema_validation_success(
    schema: Dict[str, Any], data: Dict[str, Any]
):
    validator = PydanticSchemaParser(schema)
    validated_data = validator.validate(data, base_url="http://example.com")
    assert validated_data == validator.model(**data).model_dump()


from typing import Any, Dict
import pytest
import test.parser.schema_with_required_fields as schemas
from harambe.parser.parser import (
    PydanticSchemaParser,
    SchemaValidationError,
    RequiredFieldsError,
)


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            schemas.document_schema,
            {
                "title": None,  # required
                "document_url": None,  # required
            },
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
        ),
        (
            schemas.list_of_strings_schema,
            {
                "tags": [],  # required
            },
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
        ),
        (
            schemas.object_with_list_schema,
            {
                "team": {
                    "name": None,  # required
                    "members": ["test"],
                },
            },
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
        ),
        (
            schemas.list_of_lists_schema,
            {
                "matrix": [[]],  # required
            },
        ),
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
        ),
        (
            schemas.datetime_schema,
            {
                "event": {
                    "name": None,  # required
                    "date": "05/29/2024 02:00:00 PM",
                },
            },
        ),
        (
            schemas.phone_number_schema,
            {
                "contact": {
                    "name": None,  # required
                    "phone": "11111111111",  # required
                },
            },
        ),
        (
            schemas.url_schema,
            {
                "resource": {
                    "name": "",  # required
                    "link": "http://example.com",  # required
                },
            },
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
        ),
    ],
)
def test_pydantic_schema_validation_error_fail(
    schema: Dict[str, Any], data: Dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises((SchemaValidationError, RequiredFieldsError)):
        validator.validate(data, base_url="http://example.com")


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
                    "street": "",
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
                                "team_name": "",
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

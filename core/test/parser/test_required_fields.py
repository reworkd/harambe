from functools import partial
from typing import Any, Dict

import pytest

from harambe_core.parser.parser import (
    SchemaParser,
    SchemaValidationError,
)
from test.parser.mock_schemas.load_schema import load_schema

load_schema = partial(load_schema, make_all_required=True)


@pytest.mark.parametrize(
    "schema, data",
    [
        (
                load_schema("government_contracts"),
                {
                    "title": None,  # required
                    "document_url": None,  # required
                },
        ),
        (
                load_schema("documents"),
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
                load_schema("contact", exclude="last_name,street,zip"),
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
                load_schema("list_of_strings"),
                {
                    "tags": [],  # required
                },
        ),
        (
                load_schema("list_of_objects"),
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
                load_schema("object_with_list"),
                {
                    "team": {
                        "name": None,  # required
                        "members": ["test"],
                    },
                },
        ),
        (
                load_schema("object_with_list_of_objects"),
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
                load_schema("list_of_lists"),
                {
                    "matrix": [[]],  # required
                },
        ),
        (
                load_schema("nested_lists_and_objects"),
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
                load_schema("datetime"),
                {
                    "event": {
                        "name": None,  # required
                        "date": "05/29/2024 02:00:00 PM",
                    },
                },
        ),
        (
                load_schema("phone_number"),
                {
                    "contact": {
                        "name": None,  # required
                        "phone": "11111111111",  # required
                    },
                },
        ),
        (
                load_schema("url"),
                {
                    "resource": {
                        "name": "",  # required
                        "link": "http://example.com",  # required
                    },
                },
        ),
        (
                load_schema("object_with_nested_types"),
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
                load_schema("list_with_nested_types"),
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
    validator = SchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data",
    [
        (
                load_schema("document"),
                {
                    "title": "Document Title",  # required
                    "document_url": "http://example.com/doc",  # required
                },
        ),
        (
                load_schema("documents"),
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
                load_schema("contact", exclude="last_name,street,zip"),
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
                load_schema("list_of_strings"),
                {
                    "tags": ["tag1", "tag2"],  # required
                },
        ),
        (
                load_schema("list_of_objects", exclude="email"),
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
                load_schema("object_with_list"),
                {
                    "team": {
                        "name": "Dev Team",  # required
                        "members": ["Alice", "Bob"],  # required
                    },
                },
        ),
        (
                load_schema("object_with_list_of_objects", exclude="e,b"),
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
                load_schema("list_of_lists"),
                {
                    "matrix": [[1, 2], [3, 4]],  # required
                },
        ),
        (
                load_schema("nested_lists_and_objects", exclude="team_name"),
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
                load_schema("datetime"),
                {
                    "event": {
                        "name": "Launch",  # required
                        "date": "2024-09-24T12:00:00Z",
                    },
                },
        ),
        (
                load_schema("phone_number"),
                {
                    "contact": {
                        "name": "Support",  # required
                        "phone": "+1234567890",  # required
                    },
                },
        ),
        (
                load_schema("url"),
                {
                    "resource": {
                        "name": "Website",  # required
                        "link": "http://example.com",  # required
                    },
                },
        ),
        (
                load_schema("object_with_nested_types", exclude="contact,event_date,website"),
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
                load_schema("list_with_nested_types"),
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
    validator = SchemaParser(schema)
    validated_data = validator.validate(data, base_url="http://example.com")
    assert validated_data == validator.model(**data).model_dump()

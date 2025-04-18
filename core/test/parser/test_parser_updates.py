from typing import Any

import pytest

from harambe_core.parser.parser import SchemaParser, SchemaValidationError
from test.parser.mock_schemas.load_schema import load_schema


@pytest.mark.parametrize(
    "schema, data, expected",
    [
        # Test datetime schema
        (
            load_schema("datetime"),
            {"event": {"name": "Conference", "date": "2024-06-27 10:00:00"}},
            {"event": {"name": "Conference", "date": "2024-06-27T10:00:00"}},
        ),
        # Test datetime schema with extra spaces
        (
            load_schema("datetime"),
            {"event": {"name": "   Conference", "date": "    2024-06-27 10:00:00    "}},
            {"event": {"name": "Conference", "date": "2024-06-27T10:00:00"}},
        ),
        # # Test phone number schema
        (
            load_schema("phone_number"),
            {"contact": {"name": "John Doe", "phone": "+1 (800) 555-1234"}},
            {"contact": {"name": "John Doe", "phone": "+1 800-555-1234"}},
        ),
        # # Test URL schema
        (
            load_schema("url"),
            {"resource": {"name": "API Documentation", "link": "/docs"}},
            {
                "resource": {
                    "name": "API Documentation",
                    "link": "http://example.com/docs",
                }
            },
        ),
        # # Test URL schema with extra spaces
        (
            load_schema("url"),
            {"  resource  ": {"  name   ": "  API Documentation  ", "link": " /docs "}},
            {
                "resource": {
                    "name": "API Documentation",
                    "link": "http://example.com/docs",
                }
            },
        ),
        # # Test object with nested types
        (
            load_schema("object_with_nested_types"),
            {
                "profile": {
                    "user": "johndoe",
                    "contact": "+1 (800) 555-1234",
                    "event_date": "2024-06-27 10:00:00",
                    "website": "/profile",
                }
            },
            {
                "profile": {
                    "user": "johndoe",
                    "contact": "+1 800-555-1234",
                    "event_date": "2024-06-27T10:00:00",
                    "website": "http://example.com/profile",
                }
            },
        ),
        # # Test list with nested types
        (
            load_schema("list_with_nested_types"),
            {
                "events": [
                    {
                        "name": "Event 1",
                        "dates": ["2024-06-27 10:00:00", "2024-07-01 15:00:00"],
                        "contacts": ["+1 (800) 555-1234", "+1 (800) 555-5678"],
                        "links": ["/event1", "/event1details"],
                    }
                ]
            },
            {
                "events": [
                    {
                        "name": "Event 1",
                        "dates": ["2024-06-27T10:00:00", "2024-07-01T15:00:00"],
                        "contacts": ["+1 800-555-1234", "+1 800-555-5678"],
                        "links": [
                            "http://example.com/event1",
                            "http://example.com/event1details",
                        ],
                    }
                ]
            },
        ),
        # # Test list with nested types with extra spaces
        (
            load_schema("list_with_nested_types"),
            {
                "events": [
                    {
                        "name": "  Event 1     ",
                        "dates": ["   2024-06-27 10:00:00 ", "   2024-07-01 15:00:00"],
                        "contacts": ["+1 (800) 555-1234   ", "+1 (800) 555-5678"],
                        "links": ["/event1   ", "   /event1details"],
                    }
                ]
            },
            {
                "events": [
                    {
                        "name": "Event 1",
                        "dates": ["2024-06-27T10:00:00", "2024-07-01T15:00:00"],
                        "contacts": ["+1 800-555-1234", "+1 800-555-5678"],
                        "links": [
                            "http://example.com/event1",
                            "http://example.com/event1details",
                        ],
                    }
                ]
            },
        ),
    ],
)
def test_parser_with_updated_types_success(
    schema: dict[str, Any], data: dict[str, Any], expected: dict[str, Any]
) -> None:
    validator = SchemaParser(schema)
    validated_data = validator.validate(data, base_url="http://example.com")
    assert validated_data == expected


@pytest.mark.parametrize(
    "schema, data",
    [
        # Invalid datetime
        (
            load_schema("datetime"),
            {"event": {"name": "Conference", "date": "InvalidDate"}},
        ),
        # Invalid phone number
        (
            load_schema("phone_number"),
            {"contact": {"name": "John Doe", "phone": "12345"}},
        ),
        # Invalid URL
        (
            load_schema("url"),
            {"resource": {"name": "API Documentation", "link": "invalid-url"}},
        ),
        # Invalid object with nested types
        (
            load_schema("object_with_nested_types"),
            {
                "profile": {
                    "user": "johndoe",
                    "contact": "12345",
                    "event_date": "InvalidDate",
                    "website": "invalid-url",
                }
            },
        ),
        # Invalid list with nested types
        (
            load_schema("list_with_nested_types"),
            {
                "events": [
                    {
                        "name": "Event 1",
                        "dates": ["2024-06-27T10:00:00Z", "InvalidDate"],
                        "contacts": ["+1-800-555-1234", "12345"],
                        "links": ["https://event1.com", "invalid-url"],
                    }
                ]
            },
        ),
    ],
)
def parser_with_updated_types_error(
    schema: dict[str, Any], data: dict[str, Any]
) -> None:
    validator = SchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")

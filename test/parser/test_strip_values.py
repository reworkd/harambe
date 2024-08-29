from typing import Any

import pytest

from harambe.parser.parser import trim_keys_and_strip_values


@pytest.mark.parametrize(
    "data, expected",
    [
        # Simple string strip test
        (
            {
                "name": " John Doe",
                "phone_number": "  +1 (800) 555-1234  ",
                "email": "  ktrevino@dcsdk12.org ",
            },
            {
                "name": "John Doe",
                "phone_number": "+1 (800) 555-1234",
                "email": "ktrevino@dcsdk12.org",
            },
        ),
        # Simple string with space symbols strip test
        (
            {
                "name": " \u00a0 John Doe\u00a0",
                "phone_number": "  +1 (800) 555-1234  ",
                "email": "\u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 ktrevino@dcsdk12.org",
            },
            {
                "name": "John Doe",
                "phone_number": "+1 (800) 555-1234",
                "email": "ktrevino@dcsdk12.org",
            },
        ),
        # Test datetime string stripping
        (
            {"event": {"name": "  Conference  ", "date": "  2024-06-27 10:00:00  "}},
            {"event": {"name": "Conference", "date": "2024-06-27 10:00:00"}},
        ),
        # Nested dictionary
        (
            {"contact": {"name": "  John Doe  ", "phone": "  +1 (800) 555-1234  "}},
            {"contact": {"name": "John Doe", "phone": "+1 (800) 555-1234"}},
        ),
        # URL formatting and stripping
        (
            {"resource": {"name": "  API Documentation  ", "link": "  /docs  "}},
            {
                "resource": {
                    "name": "API Documentation",
                    "link": "/docs",
                }
            },
        ),
        # Complex nested structure with various types of data
        (
            {
                "profile": {
                    "user": "  johndoe  ",
                    "contact": "  +1 (800) 555-1234  ",
                    "event_date": "  2024-06-27 10:00:00  ",
                    "website": "  /profile  ",
                }
            },
            {
                "profile": {
                    "user": "johndoe",
                    "contact": "+1 (800) 555-1234",
                    "event_date": "2024-06-27 10:00:00",
                    "website": "/profile",
                }
            },
        ),
        # List of events with nested structures
        (
            {
                "events": [
                    {
                        "name": "  Event 1  ",
                        "dates": ["  2024-06-27 10:00:00  ", "  2024-07-01 15:00:00  "],
                        "contacts": ["  +1 (800) 555-1234  ", "  +1 (800) 555-5678  "],
                        "links": ["  /event1  ", "  /event1details  "],
                    }
                ]
            },
            {
                "events": [
                    {
                        "name": "Event 1",
                        "dates": ["2024-06-27 10:00:00", "2024-07-01 15:00:00"],
                        "contacts": ["+1 (800) 555-1234", "+1 (800) 555-5678"],
                        "links": [
                            "/event1",
                            "/event1details",
                        ],
                    }
                ]
            },
        ),
        # Edge case: Empty strings and mixed types
        (
            {
                "profile": {
                    "user": "   ",
                    "contact": None,
                    "event_date": "",
                    "website": "/profile",
                    "likes": [],
                    "stats": {},
                }
            },
            {
                "profile": {
                    "user": None,
                    "contact": None,
                    "event_date": None,
                    "website": "/profile",
                    "likes": [],
                    "stats": {},
                }
            },
        ),
        # Edge case: String with only spaces
        (
            {"user": "    ", "active": True},
            {"user": None, "active": True},
        ),
        # List of strings with spaces
        (
            {"tags": ["  tag1  ", "  tag2  ", "  tag3  "]},
            {"tags": ["tag1", "tag2", "tag3"]},
        ),
    ],
)
def test_strip_all_values(data: dict[str, Any], expected: dict[str, Any]) -> None:
    output_data = trim_keys_and_strip_values(data)
    assert output_data == expected

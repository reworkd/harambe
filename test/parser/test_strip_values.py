from typing import Any

import pytest
from harambe.parser.parser import strip_all_values


@pytest.mark.parametrize(
    "data, expected",
    [
        # Simple string strip test
        (
            {"name": "  John Doe", "phone_number": "  +1 (800) 555-1234  "},
            {"name": "John Doe", "phone_number": "+1 (800) 555-1234"},
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
                    "user": "",
                    "contact": None,
                    "event_date": "",
                    "website": "/profile",
                    "likes": [],
                    "stats": {},
                }
            },
        ),
        # Edge case: String with only spaces
        (
            {"user": "    ", "active": True},
            {"user": "", "active": True},
        ),
        # List of strings with spaces
        (
            {"tags": ["  tag1  ", "  tag2  ", "  tag3  "]},
            {"tags": ["tag1", "tag2", "tag3"]},
        ),
    ],
)
def test_strip_all_values(data: dict[str, Any], expected: dict[str, Any]) -> None:
    output_data = strip_all_values(data)
    assert output_data == expected

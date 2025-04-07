from typing import Any, Dict

import pytest

from harambe_core.errors import SchemaValidationError
from harambe_core.parser.parser import SchemaParser
from test.parser.mock_schemas.load_schema import load_schema

government_contracts = load_schema("government_contracts")


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": None,
            "title": None,
            "status": None,
            "description": None,
            "location": None,
            "type": None,
            "category": None,
            "posted_date": None,
            "due_date": None,
            "buyer_name": None,
            "buyer_contact_name": None,
            "buyer_contact_email": None,
            "buyer_contact_number": None,
            "attachments": None,
            "procurement_items": None,
        },
        {
            "id": "",
            "title": "",
            "status": "",
            "description": "",
            "location": "",
            "type": "",
            "category": "",
            "posted_date": "",
            "due_date": "",
            "buyer_name": "",
            "buyer_contact_name": "",
            "buyer_contact_email": "",
            "buyer_contact_number": "",
            "attachments": [],
            "procurement_items": [],
        },
        {
            "id": "",
            "title": "",
            "status": "",
            "description": "",
            "location": "",
            "type": "",
            "category": "",
            "posted_date": "",
            "due_date": "",
            "buyer_name": "",
            "buyer_contact_name": "",
            "buyer_contact_email": "",
            "buyer_contact_number": "",
            "attachments": [{"title": "", "url": ""}],
            "procurement_items": [
                {
                    "code_type": "",
                    "code": "",
                    "code_description": "",
                    "description": "",
                }
            ],
        },
    ],
)
def test_pydantic_schema_validation_error_fail(data: Dict[str, Any]) -> None:
    validator = SchemaParser(government_contracts)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "data",
    [
        {
            "id": "123",
            "title": None,
            "status": None,
            "description": None,
            "location": None,
            "type": None,
            "category": None,
            "posted_date": None,
            "due_date": None,
            "buyer_name": None,
            "buyer_contact_name": None,
            "buyer_contact_email": None,
            "buyer_contact_number": None,
            "attachments": [{"title": "Attachment 1", "url": None}],
            "procurement_items": [],
        },
        {
            "id": "123",
            "title": "",
            "status": "",
            "description": "",
            "location": "",
            "type": "",
            "category": "",
            "posted_date": "",
            "due_date": "",
            "buyer_name": "",
            "buyer_contact_name": "",
            "buyer_contact_email": "",
            "buyer_contact_number": "",
            "attachments": [{"title": "Attachment 1", "url": ""}],
            "procurement_items": [
                {
                    "code_type": "",
                    "code": "",
                    "code_description": "",
                    "description": "Something",
                }
            ],
        },
    ],
)
def test_pydantic_schema_validation_success(data: Dict[str, Any]):
    validator = SchemaParser(government_contracts)
    validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "data",
    [
        {"group": "Team", "members": [{}]},
        {
            "group": "",
            "members": [
                {
                    "name": "",
                    "age": None,
                },
            ],
        },
    ],
)
def test_with_empty_objects(data):
    schema = {
        "group": {"type": "string"},
        "members": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        },
    }

    with pytest.raises(SchemaValidationError):
        validator = SchemaParser(schema)
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "data",
    [
        {"group": "Team", "members": [{"name": None, "age": None}]},
        {
            "group": "Team",
            "members": [
                {
                    "name": "",
                    "age": None,
                },
            ],
        },
        {
            "group": "Team",
            "members": [
                {
                    "name": "Adam",
                    "age": 29,
                },
                {
                    "name": "",
                    "age": None,
                },
            ],
        },
    ],
)
def test_with_objects(data):
    schema = {
        "group": {"type": "string"},
        "members": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        },
    }

    validator = SchemaParser(schema)
    res = validator.validate(data, base_url="http://example.com")
    assert res["group"] == "Team"


@pytest.mark.parametrize(
    "strings",
    [
        (
                ["", None, None],
                [None, None],
                ["a", "  "],
                ["a", "b", "c", ""],
        )
    ],
)
def test_with_empty_literals(strings):
    schema = {
        "strings": {"type": "array", "items": {"type": "integer"}},
    }

    with pytest.raises(SchemaValidationError):
        validator = SchemaParser(schema)
        validator.validate({"strings": strings}, base_url="http://example.com")

@pytest.mark.parametrize("url", ["", None])
def test_nullable_object(url):
    schema = {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "address": {"type": "object", "properties": {"street": {"type": "string"}}},
        "profile_url": {"type": "url"},
    }
    data = {
        "name": "Adam",
        "age": 29,
        "address": None,
        "profile_url": url,
    }

    validator = SchemaParser(schema)
    res = validator.validate(data, base_url="http://example.com")
    assert res["address"] is None
    assert res["profile_url"] is None


def test_nullable_object_sub_schema():
    schema = load_schema("object_with_nested_objects")
    data = {
        "profile": {
            "id": 123,
            "personal_info": None,
        }
    }

    validator = SchemaParser(schema)
    res = validator.validate(data, base_url="http://example.com")
    assert res["profile"]["id"] == 123
    assert res["profile"]["personal_info"] is None
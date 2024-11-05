import pytest

from harambe_core import SchemaParser
from test.parser.mock_schemas.load_schema import load_schema


@pytest.fixture
def schema() -> dict:
    return {
        "degree": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
    }


@pytest.fixture
def data() -> dict:
    return {
        "degree": "Bachelor of Science: Computer Science",
        "first_name": "Adam",
        "last_name": "Watkins",
    }


def test_single_computed_field(schema, data) -> None:
    schema["full_name"] = {
        "type": "string",
        "expression": "CONCAT(first_name, ' ', last_name)",
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["full_name"] == "Adam Watkins"


def test_computed_of_computed(schema, data) -> None:
    schema.update(
        {
            "full_name": {
                "type": "string",
                "expression": "CONCAT(first_name, ' ', last_name)",
            },
            "slug": {
                "type": "string",
                "expression": "CONCAT_WS('_', full_name, degree)",
            },
        }
    )

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["full_name"] == "Adam Watkins"
    assert output_data["slug"] == "Adam Watkins_Bachelor of Science: Computer Science"


def test_self_reference(schema, data) -> None:
    schema["full_name"] = {
        "type": "string",
        "expression": "COALESCE(full_name, CONCAT(first_name, ' ', last_name))",
    }

    data["full_name"] = "John Doe"

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["full_name"] == "John Doe"


@pytest.mark.skip("TODO: implement nested index access")
def test_nested_reference(schema, data):
    schema["children"] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "middle_name": {
                    "type": "string",
                    "expression": "COALESCE(children.middle_name, 'G')",
                },
                "last_name": {"type": "string", "expression": "last_name"},
            },
        },
    }

    data["children"] = [
        {
            "first_name": "Alice",
        },
        {
            "first_name": "Bob",
            "middle_name": "H",
        },
    ]

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data == {
        "children": [
            {
                "first_name": "Alice",
                "middle_name": "G",
                "last_name": "Watkins",
            },
            {
                "first_name": "Bob",
                "middle_name": "H",
                "last_name": "Watkins",
            },
        ]
    }


def test_parser_computed_pk():
    schema_ = load_schema("computed_pk")
    schema_["$primary_key"] = "CONCAT(resource.name, '_', resource.link)"
    data = {
        "resource": {
            "name": "API Documentation",
            "link": "https://reworkd.ai/docs",
        }
    }

    validator = SchemaParser(schema_)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["$primary_key"] == "API Documentation_https://reworkd.ai/docs"


def test_computed_on_nullable_field(schema, data):
    data["degree"] = ""
    schema["degree"]["expression"] = "UPPER(degree)"

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["degree"] is None


def test_computed_on_required_field(schema, data):
    data["degree"] = None
    schema["degree"]["expression"] = "UPPER('BA in Social Studies')"
    schema["degree"]["required"] = True

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["degree"] == "BA IN SOCIAL STUDIES"

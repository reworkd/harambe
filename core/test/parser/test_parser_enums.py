import pytest

from harambe_core import SchemaParser
from harambe_core.errors import SchemaValidationError


@pytest.fixture
def schema() -> dict:
    return {
        "name": {"type": "string"},
        "status": {
            "type": "enum",
            "variants": ["active", "inactive", "pending"],
        },
    }


@pytest.mark.parametrize("value", ["active", "PENDING", "Inactive"])
def test_required_enums(value, schema) -> None:
    schema["status"]["required"] = True

    data = {
        "name": "Test Name",
        "status": value,
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["status"] == (value.lower() if value else None)


def test_required_enum_missing(schema) -> None:
    schema["status"]["required"] = True

    data = {
        "name": "Test Name",
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize("value", ["active", "PENDING", "Inactive", None])
def test_optional_enum(value, schema) -> None:
    schema["status"]["required"] = False

    data = {
        "name": "Test Name",
        "status": value,
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["status"] == (value.lower() if value else None)


@pytest.mark.parametrize("value", ["active", "PENDING", "Inactive"])
def test_enum_in_list(value, schema) -> None:
    schema["status"]["type"] = "array"
    schema["status"]["items"] = {
        "type": "enum",
        "variants": ["active", "inactive", "pending"],
    }

    data = {
        "name": "Test Name",
        "status": [value, value],
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["status"] == [value.lower(), value.lower()]



def test_null_enum_in_array(schema) -> None:
    schema["status"]["type"] = "array"
    schema["status"]["items"] = {
        "type": "enum",
        "variants": ["active", "inactive", "pending"],
    }

    data = {
        "name": "Test Name",
        "status": ['active', None],
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")

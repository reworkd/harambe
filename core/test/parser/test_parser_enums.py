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


@pytest.mark.parametrize("value", ["active", "PENDING", "Inactive", None])
def test_required_enums(value, schema) -> None:
    schema["status"]["required"] = True

    data = {
        "name": "Test Name",
        "status": value,
    }

    validator = SchemaParser(schema)

    if value is None:
        with pytest.raises(SchemaValidationError):
            validator.validate(data, base_url="http://example.com")

        return

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["status"] == (value.lower() if value else None)


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


@pytest.mark.parametrize("required", [True, False])
@pytest.mark.parametrize("value", ["active", "PENDING", "Inactive", None])
def test_enum_in_list(value, schema, required) -> None:
    schema["status"]["required"] = required
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

    # Array items should never be none
    if value is None:
        with pytest.raises(SchemaValidationError):
            validator.validate(data, base_url="http://example.com")

        return

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["status"] == [value.lower(), value.lower()]

import pytest

from harambe_core import SchemaParser
from harambe_core.errors import SchemaValidationError
from harambe_core.parser.constants import RESERVED_PREFIX
from test.parser.mock_schemas.load_schema import load_schema


def test_pydantic_reserved_fields():
    validator = SchemaParser(load_schema("reserved_pydantic_fields"))
    res = validator.validate(
        {
            "model_config": [1, 2],
            "model_type": "example_type",
            "model_name": "example_name",
            "model_id": 1,
            "model_dump": "example_dump",
            "model_json": {
                "model_validate": "value1",
                "model_dump": 1,
                "model_config": [1, 2],
            },
        },
        base_url="http://example.com",
    )

    assert res.get("model_config") == [1, 2]
    assert res.get("model_type") == "example_type"
    assert res.get("model_name") == "example_name"
    assert res.get("model_id") == 1
    assert res.get("model_dump") == "example_dump"
    assert res.get("model_extra") == "example_name_example_type"
    assert res.get("model_json") == {
        "model_validate": "value1",
        "model_dump": 1,
        "model_config": [1, 2],
    }


def test_python_reserved_fields():
    validator = SchemaParser(load_schema("reserved_python_fields"))
    res = validator.validate(
        {
            "def": "example_def",
            "class": "example_class",
            "return": "example_return",
            "lambda": "example_lambda",
            "add": 5,
            "del": 3,
            "from": 1,
        },
        base_url="http://example.com",
    )

    assert res.get("def") == "example_def"
    assert res.get("class") == "example_class"
    assert res.get("return") == "example_return"
    assert res.get("lambda") == "example_lambda"
    assert res.get("add") == 5
    assert res.get("del") == 3
    assert res.get("from") == 1
    assert res.get("import") == "example_import_example_def_example_class"


def test_reserved_prefix_not_shown_in_error_message():
    validator = SchemaParser(load_schema("reserved_pydantic_fields"))

    with pytest.raises(SchemaValidationError) as excinfo:
        validator.validate(
            {
                "model_config": 1,
            },
            base_url="http://example.com",
        )

    assert RESERVED_PREFIX not in str(excinfo.value)
    assert "model_config" in str(excinfo.value)

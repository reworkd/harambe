from typing import Optional

import pytest
from pydantic import BaseModel, ValidationError

from harambe.parser.type_string import ParserTypeString


class MyModel(BaseModel):
    my_field: Optional[ParserTypeString] = None


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"my_field": "hello"}, "hello"),
        ({"my_field": ""}, None),
        ({"my_field": "   "}, "   "),
        ({"my_field": None}, None),
        ({}, None),
    ],
)
def test_parser_type_string_success(data, expected):
    model = MyModel(**data)
    assert model.my_field == expected


@pytest.mark.parametrize(
    "data, expected_error",
    [
        ({"my_field": 123}, "Input should be a valid string"),
        ({"my_field": False}, "Input should be a valid string"),
        ({"my_field": True}, "Input should be a valid string"),
        ({"my_field": ["list"]}, "Input should be a valid string"),
        ({"my_field": {"key": "value"}}, "Input should be a valid string"),
    ],
)
def test_parser_type_string_validation_error(data, expected_error):
    with pytest.raises(ValidationError) as exc_info:
        MyModel(**data)
    assert expected_error in str(exc_info.value)

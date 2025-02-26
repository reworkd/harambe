import pytest
from pydantic import BaseModel, ValidationError

from harambe_core.parser.type_number import ParserTypeNumber


class _TestModel(BaseModel):
    value: ParserTypeNumber


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("1,000.00", 1000.00),
        ("1.00", 1.0),
        ("1,000,000.00", 1000000.00),
        ("1000.00", 1000.00),
        ("1000", 1000.00),
        (1000, 1000.00),
        (1000.00, 1000.00),
        ("-1,234.56", -1234.56),
        ("0.1", 0.1),
        (".1", 0.1),
        (15604980646, 15604980646)
    ],
)
def test_flexible_float_success(input_value, expected_output):
    model = _TestModel(value=input_value)
    assert model.value == pytest.approx(expected_output)


@pytest.mark.parametrize(
    "input_value",
    [
        "abc",
        "one hundred",
        "1.00.00",
        "1.2.3",
        "",
        None,
        {},
        [],
    ],
)
def test_flexible_float_failure(input_value):
    with pytest.raises(ValidationError):
        _TestModel(value=input_value)

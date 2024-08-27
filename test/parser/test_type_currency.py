import pytest
from pydantic import BaseModel, ValidationError

from harambe.parser.type_currency import ParserTypeCurrency


class TestModel(BaseModel):
    value: ParserTypeCurrency()


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("$1,000.00", 1000.00),
        ("€1.00", 1.0),
        ("£1,000,000.00", 1000000.00),
        ("¥1000.00", 1000.00),
        ("₹1000", 1000.00),
        (1000, 1000.00),
        (1000.00, 1000.00),
        ("-¥1,234.56", -1234.56),
        ("$0.1", 0.1),
        ("€.1", 0.1),
        ("1000", 1000.00),
        ("$1,234.5678", 1234.5678),
        ("   $1,234  ", 1234.0),
        ("   $ 1,234  ", 1234.0),
        ("1.234 €", 1234.0),
        ("1.234€", 1234.0),
        ("€1.234", 1234.0),
        ("1,234$", 1234.0),
        ("1,234 $", 1234.0),
        ("1.234,45", 1234.45),
        ("1.234.456,00", 1234456.00),
        ("1.000.000", 1000000.00),
        ("Starting at: 12:00", 12.0),
        ("Starting At 12.99", 12.99),
        ("From 399.99", 399.99),
    ],
)
def test_flexible_currency_success(input_value, expected_output):
    model = TestModel(value=input_value)
    assert model.value == pytest.approx(expected_output)


@pytest.mark.parametrize(
    "input_value",
    [
        "abc",
        "one hundred",
        "1.00.00",
        "1.2.3",
        "Begin 12.00 End 23.00",
        "Between 12.00 And 23.00",
        "From 12.00 To 23.00",
        "",
        None,
        {},
        [],
    ],
)
def test_flexible_float_failure(input_value):
    with pytest.raises(ValidationError):
        TestModel(value=input_value)

import pytest
from pydantic import BaseModel, ValidationError

from harambe_core.parser.type_currency import ParserTypeCurrencyType


class _TestModel(BaseModel):
    value: ParserTypeCurrencyType


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("$1,000.00", {"currency": "USD", "currency_symbol": "$", "amount": 1000.00}),
        ("€1.00", {"currency": "EUR", "currency_symbol": "€", "amount": 1.0}),
        (
            "£1,000,000.00",
            {"currency": "GBP", "currency_symbol": "£", "amount": 1000000.00},
        ),
        ("¥1000.00", {"currency": "JPY", "currency_symbol": "¥", "amount": 1000.00}),
        ("₹1000", {"currency": "INR", "currency_symbol": "₹", "amount": 1000.00}),
        (1000, {"currency": None, "currency_symbol": None, "amount": 1000.00}),
        (1000.00, {"currency": None, "currency_symbol": None, "amount": 1000.00}),
        ("-¥1,234.56", {"currency": "JPY", "currency_symbol": "¥", "amount": -1234.56}),
        ("$0.1", {"currency": "USD", "currency_symbol": "$", "amount": 0.1}),
        ("€.1", {"currency": "EUR", "currency_symbol": "€", "amount": 0.1}),
        ("1000", {"currency": None, "currency_symbol": None, "amount": 1000.00}),
        (1000, {"currency": None, "currency_symbol": None, "amount": 1000.00}),
        (
            "$1,234.5678",
            {"currency": "USD", "currency_symbol": "$", "amount": 1234.5678},
        ),
        ("   $1,234  ", {"currency": "USD", "currency_symbol": "$", "amount": 1234.0}),
        ("   $ 1,234  ", {"currency": "USD", "currency_symbol": "$", "amount": 1234.0}),
        ("1.234 €", {"currency": "EUR", "currency_symbol": "€", "amount": 1234.0}),
        ("1.234€", {"currency": "EUR", "currency_symbol": "€", "amount": 1234.0}),
        ("€1.234", {"currency": "EUR", "currency_symbol": "€", "amount": 1234.0}),
        ("1,234$", {"currency": "USD", "currency_symbol": "$", "amount": 1234.0}),
        ("1,234 $", {"currency": "USD", "currency_symbol": "$", "amount": 1234.0}),
        ("1.234,45", {"currency": None, "currency_symbol": None, "amount": 1234.45}),
        (
            "1.234.456,00",
            {"currency": None, "currency_symbol": None, "amount": 1234456.00},
        ),
        (
            "1.000.000",
            {"currency": None, "currency_symbol": None, "amount": 1000000.00},
        ),
        (
            "Starting At 12.99",
            {"currency": None, "currency_symbol": None, "amount": 12.99},
        ),
        ("From 399.99", {"currency": None, "currency_symbol": None, "amount": 399.99}),
        ("0.0004 $", {"currency": "USD", "currency_symbol": "$", "amount": 0.0004}),
        (
            "Price Not Available",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (
            "Unavailable Price",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (
            "Price Upon Request",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (
            "Contact for Price",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (
            "Request a Quote",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        ("TDB", {"currency": None, "currency_symbol": None, "amount": None}),
        ("N/A", {"currency": None, "currency_symbol": None, "amount": None}),
        (
            "Price Not Disclosed",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        ("Out of Stock", {"currency": None, "currency_symbol": None, "amount": None}),
        ("Sold Out", {"currency": None, "currency_symbol": None, "amount": None}),
        (
            "Pricing Not Provided",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        ("Not Priced", {"currency": None, "currency_symbol": None, "amount": None}),
        (
            "Currently Unavailable",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (
            "Ask for Pricing",
            {"currency": None, "currency_symbol": None, "amount": None},
        ),
        (None, {"currency": None, "currency_symbol": None, "amount": None}),
    ],
)
def test_currency_success(input_value, expected_output):
    model = _TestModel(value=input_value)
    assert model.value == expected_output


# Failure cases: these should raise a ValidationError
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
        "12.00 - 23.00",
        "Not a number",
        "1.234.56",
        "1,234,56",
        "$",
        "1,234.56.78",
        "123,456,12",
        "",
        {},
        [],
    ],
)
def test_currency_failure(input_value):
    with pytest.raises(ValidationError):
        _TestModel(value=input_value)

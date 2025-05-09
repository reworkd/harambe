import pytest
from pydantic import BaseModel, ValidationError

from harambe_core.parser.type_price import ParserTypePrice


class _TestModel(BaseModel):
    value: ParserTypePrice(required=False)


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (
            "$1,000.00",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 1000.00,
                "raw_price": "$1,000.00",
            },
        ),
        (
            "€1.00",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": 1.00,
                "raw_price": "€1.00",
            },
        ),
        (
            "£1,000,000.00",
            {
                "currency": "GBP",
                "raw_currency": "£",
                "amount": 1000000.00,
                "raw_price": "£1,000,000.00",
            },
        ),
        (
            "-¥1000.00",
            {
                "currency": "JPY",
                "raw_currency": "¥",
                "amount": -1000.00,
                "raw_price": "-¥1000.00",
            },
        ),
        (
            "₹1000",
            {
                "currency": "INR",
                "raw_currency": "₹",
                "amount": 1000.00,
                "raw_price": "₹1000",
            },
        ),
        (
            1000,
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1000.00,
                "raw_price": "1000",
            },
        ),
        (
            1000.0,
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1000.0,
                "raw_price": "1000.0",
            },
        ),
        (
            "¥-1,234.56",
            {
                "currency": "JPY",
                "raw_currency": "¥",
                "amount": -1234.56,
                "raw_price": "¥-1,234.56",
            },
        ),
        (
            "$0.1",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 0.1,
                "raw_price": "$0.1",
            },
        ),
        (
            "€.1",
            {"currency": "EUR", "raw_currency": "€", "amount": 0.1, "raw_price": "€.1"},
        ),
        (
            "1000",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1000.00,
                "raw_price": "1000",
            },
        ),
        (
            "$1,234.5678",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 1234.5678,
                "raw_price": "$1,234.5678",
            },
        ),
        (
            "   $1,234  ",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 1234.0,
                "raw_price": "$1,234",
            },
        ),
        (
            "   USD -1,234.56  ",
            {
                "currency": "USD",
                "raw_currency": "USD",
                "amount": -1234.56,
                "raw_price": "USD -1,234.56",
            },
        ),
        (
            "1.234 €",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": 1234.0,
                "raw_price": "1.234 €",
            },
        ),
        (
            "1.234 EUR",
            {
                "currency": "EUR",
                "raw_currency": "EUR",
                "amount": 1234.0,
                "raw_price": "1.234 EUR",
            },
        ),
        (
            "-€1.234",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": -1234.0,
                "raw_price": "-€1.234",
            },
        ),
        (
            "1,234$",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 1234.0,
                "raw_price": "1,234$",
            },
        ),
        (
            " $\xa01,234 ",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 1234.0,
                "raw_price": "$\xa01,234",
            },
        ),
        (
            "1.234,45",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1234.45,
                "raw_price": "1.234,45",
            },
        ),
        (
            "1.234.456,00",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1234456.00,
                "raw_price": "1.234.456,00",
            },
        ),
        (
            "1.000.000",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 1000000.00,
                "raw_price": "1.000.000",
            },
        ),
        (
            "Starting At 12.99",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 12.99,
                "raw_price": "Starting At 12.99",
            },
        ),
        (
            "From 399.99",
            {
                "currency": None,
                "raw_currency": None,
                "amount": 399.99,
                "raw_price": "From 399.99",
            },
        ),
        (
            "0.0004 $",
            {
                "currency": "USD",
                "raw_currency": "$",
                "amount": 0.0004,
                "raw_price": "0.0004 $",
            },
        ),
        (
            "-€23,19",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": -23.19,
                "raw_price": "-€23,19",
            },
        ),
        (
            "48,99   €",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": 48.99,
                "raw_price": "48,99   €",
            },
        ),
        (
            "€\xa026,49",
            {
                "currency": "EUR",
                "raw_currency": "€",
                "amount": 26.49,
                "raw_price": "€\xa026,49",
            },
        ),
    ],
)
def test_price_success(input_value, expected_output):
    model = _TestModel(value=input_value)

    assert model.value == expected_output


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
        "1.234.56",  # Should not use dot for cents given its used in the thousands
        "1,234,56",  # Should not use comma for the cents given its used in the thousands
        "$",
        "1,234.56.78",
        ".123,456,12",
        "$100 €200",
    ],
)
def test_price_failure(input_value):
    with pytest.raises(ValidationError):
        _TestModel(value=input_value)


@pytest.mark.parametrize(
    "value",
    ["", None, "          \n "],
)
def test_required_price(value):
    class RequiredModel(BaseModel):
        value: ParserTypePrice(required=True)

    with pytest.raises(ValidationError):
        RequiredModel(value=value)

    model = RequiredModel(value="$100")
    assert model.value["amount"] == 100.0
    assert model.value["currency"] == "USD"

import pytest
from harambe_core import SchemaParser
from harambe_core.errors import SchemaValidationError


@pytest.fixture
def schema() -> dict:
    return {
        "name": {"type": "string"},
        "sale_price": {"type": "price"},
        "price": {"type": "price", "required": True},
    }


test_case_success = [
    (
        "$100.01",
        {
            "amount": 100.01,
            "currency": "USD",
            "currency_raw": "$",
            "raw_price": "$100.01",
        },
    ),
    (
        "-$10,100.01",
        {
            "amount": -10100.01,
            "currency": "USD",
            "currency_raw": "$",
            "raw_price": "-$10,100.01",
        },
    ),
    (
        "100 €",
        {
            "amount": 100.0,
            "currency": "EUR",
            "currency_raw": "€",
            "raw_price": "100 €",
        },
    ),
    (
        "100.00",
        {
            "amount": 100.0,
            "currency": None,
            "currency_raw": None,
            "raw_price": "100.00",
        },
    ),
    (
        "100.00 USD",
        {
            "currency": "USD",
            "currency_raw": "USD",
            "amount": 100.0,
            "raw_price": "100.00 USD",
        },
    ),
]
test_case_none = [
    "Price Not Available",
    "Unavailable Price",
    "Price Upon Request",
    "Contact for Price",
    "Request a Quote",
    "TDB",
    "TBD",
    "N/A",
    "Price Not Disclosed",
    "Out of Stock",
    "Sold Out",
    "Pricing Not Provided",
    "Not Priced",
    "Currently Unavailable",
    "N/A (Not Available)",
    "Ask for Pricing",
    "",
    None,
    [],
    {},
]
test_case_errors = [
    "Between $100.00 and $200.00",
    "abc",
    "10$10",
    "100 € - 2000 €",
    "USD 100.01 - 10001 USD",
    "1.00.00",
    "1,2,3",
    "1.2.3",
    "1.234.56",  # Should not use dot for cents given its used in the thousands
    "1,234,56",  # Should not use comma for the cents given its used in the thousands
]


@pytest.mark.parametrize(
    "price, expected_price",
    test_case_success,
)
def test_price_validation(price, expected_price, schema) -> None:
    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": price,
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["price"] == expected_price


@pytest.mark.parametrize("price", test_case_success)
def test_price_missing(price, schema) -> None:
    data = {
        "name": "Test Name",
        "price": price,
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize("price", test_case_errors)
def test_price_failures(price, schema) -> None:
    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": price,
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize("price", test_case_none)
def test_price_nones(price, schema) -> None:
    data = {
        "name": "Test Name",
        "sale_price": price,
        "price": "$1",
    }

    validator = SchemaParser(schema)
    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["sale_price"] is None
    assert output_data["price"] == {
        "amount": 1.0,
        "currency": "USD",
        "currency_raw": "$",
        "raw_price": "$1",
    }


@pytest.mark.parametrize("price, expected_price", test_case_success)
def test_price_in_list(price, expected_price, schema) -> None:
    schema["price"]["type"] = "array"
    schema["price"]["items"] = {
        "type": "price",
    }

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": [price, price],
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["price"] == [expected_price, expected_price]


def test_price_in_list_empty(schema) -> None:
    schema["price"]["type"] = "array"
    schema["price"]["required"] = False
    schema["price"]["items"] = {"type": "price"}

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": [],
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["price"] == []


@pytest.mark.parametrize("price", test_case_none + test_case_errors)
def test_price_in_list_required(price, schema) -> None:
    schema["price"]["type"] = "array"
    schema["price"]["required"] = False
    schema["price"]["items"] = {"type": "price"}

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": [price, price],
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize("price, expected_price", test_case_success)
def test_price_in_object(price, expected_price, schema) -> None:
    schema["price"]["type"] = "object"
    schema["price"]["properties"] = {
        "price": {"type": "price"},
    }

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": {"price": price},
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["price"] == {"price": expected_price}


@pytest.mark.parametrize("price", test_case_none)
def test_price_in_object_nones(price, schema) -> None:
    schema["price"]["type"] = "object"
    schema["price"]["properties"] = {
        "price": {"type": "price"},
    }

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": {"price": price},
    }

    validator = SchemaParser(schema)

    output_data = validator.validate(data, base_url="http://example.com")
    assert output_data["price"] == {"price": None}


@pytest.mark.parametrize("price", test_case_none + test_case_errors)
def test_price_in_object_required(price, schema) -> None:
    schema["price"]["type"] = "object"
    schema["price"]["properties"] = {
        "price": {"type": "price", "required": True},
    }

    data = {
        "name": "Test Name",
        "sale_price": None,
        "price": {"price": price},
    }

    validator = SchemaParser(schema)

    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http:~//example.com")

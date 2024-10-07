import pytest

from harambe.parser.type_phone_number import ParserTypePhoneNumber


@pytest.mark.parametrize(
    "phone_number",
    [
        "(+1) 415-155-1555",
        "11111111111",
        "911",
        "(+4) 1111111111 (Extension: 323)",
        "(956) 318-2626, Ext: 4857",  # Extension with parenthesis
        "206-555-7115, ext. 239",  # Domestic, with extension
        "212-456-7890",  # Domestic
        "456-7890",  # Local Phone Number
        "+1-212-456-7890",  # International Phone Number
        "1-212-456-7890",  # Dialed in the US
        "001-212-456-7890",  # Dialed in Germany
        "191-212-456-7890",  # Dialed in France
        "2124567890",
        "212-456-7890",
        "(212)456-7890",
        "(212)-456-7890",
        "212.456.7890",
        "212 456 7890",
        "+12124567890",
        "+12124567890",
        "+1 212.456.7890",
        "+212-456-7890",
        "1-212-456-7890",
    ],
)
def test_pydantic_type_phone_number_validate_type_success(phone_number):
    assert ParserTypePhoneNumber.validate_type(phone_number)


@pytest.mark.parametrize(
    "prefix",
    [
        "fax",
        "fax:",
        "phone",
        "Number : ",
        "Tel",
        "tel:",
        "fax:",
        "Fax:",
    ],
)
def test_pydantic_type_phone_number_rewrite(prefix):
    phone_number = "415-155-1555"
    phone_number_with_prefix = f"{prefix} {phone_number}"
    assert ParserTypePhoneNumber.validate_type(phone_number_with_prefix) == phone_number


@pytest.mark.parametrize(
    "phone_number",
    [
        # 0
        "",  # ❌ Empty string
        # 1
        "415-111-1111 Directions",  # ❌ Extra text
    ],
)
def test_pydantic_type_phone_number_validate_type_error(phone_number):
    with pytest.raises(ValueError):
        ParserTypePhoneNumber.validate_type(phone_number)

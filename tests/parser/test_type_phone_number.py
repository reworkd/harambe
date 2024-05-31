import pytest

from harambe.parser.type_phone_number import ParserTypePhoneNumber


@pytest.mark.parametrize(
    "phone_number",
    [
        # 0
        "(+1) 415-155-1555",
        # 1
        "11111111111",
        # 2
        "911",
        # 3
        "(+4) 1111111111 (Extension: 323)",
        # 4
        "206-555-7115, ext. 239",  # Domestic, with extension
        # 5
        "212-456-7890",  # Domestic
        # 6
        "456-7890",  # Local Phone Number
        # 7
        "+1-212-456-7890",  # International Phone Number
        # 8
        "1-212-456-7890",  # Dialed in the US
        # 9
        "001-212-456-7890",  # Dialed in Germany
        # 10
        "191-212-456-7890",  # Dialed in France
    ],
)
def test_pydantic_type_phone_number_validate_type_success(phone_number):
    assert ParserTypePhoneNumber.validate_type(phone_number) == phone_number


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

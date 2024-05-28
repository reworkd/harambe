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
        "206-555-7115, ext. 239",
        # 5
        "206-555-7115",
    ],
)
def test_pydantic_type_phone_number_validate_success(phone_number):
    assert ParserTypePhoneNumber.validate(phone_number) == phone_number


@pytest.mark.parametrize(
    "phone_number",
    [
        # 0
        "",  # ❌ Empty string
        # 1
        "415-111-1111 Directions",  # ❌ Extra text
    ],
)
def test_pydantic_type_phone_number_validate_error(phone_number):
    with pytest.raises(ValueError):
        ParserTypePhoneNumber.validate(phone_number)

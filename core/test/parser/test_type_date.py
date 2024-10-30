import pytest

from harambe_core.parser.type_date import ParserTypeDate


@pytest.mark.parametrize(
    "date_string",
    [
        # 0
        "05/29/2024 02:00:00 PM",
        # 1
        "5/22/2024 7:55:50 AM (EST)",
        # 2
        "May 20 2024 2:00PM",
        # 3
        "May 14, 2024 - 2:00pm",
        # 4
        "4/30/2024 09:00:02 AM (CT)",
        # 5
        "1995-12-17T03:24:00",
        # 6
        "2020-05-12T23:50:21.817Z",
        # 7
        "December 17, 1995 03:24:00",
        # 8
        "2019-01-01T00:00:00.000+00:00",
    ],
)
def test_pydantic_type_date_validate_type_success(date_string):
    assert ParserTypeDate.validate_type(date_string)


@pytest.mark.parametrize(
    "date_string",
    [
        # 0
        "",  # ❌ Empty string
        # 1
        123,  # ❌ Number instead of string
    ],
)
def test_pydantic_type_date_validate_type_error(date_string):
    with pytest.raises(ValueError):
        ParserTypeDate.validate_type(date_string)

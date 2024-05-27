import pytest

from harambe.parser.type_date import ParserTypeDate


@pytest.mark.parametrize(
    "date_string",
    [
        # 0
        "20/02/1991",
        # 1
        "2024-05-20",
        # 2
        "20 February, 1991",
        # 3
        "  20 February, 1991  ",
        # 4
        "  20 FEBRUARY, 1991  ",
        # 5
        "05/29/2024 02:00:00 PM",
        # 6
        "5/22/2024 7:55:50 AM (EST)",
        # 7
        "May 20 2024 2:00PM",
        # 8
        "May 14, 2024 - 2:00pm",
        # 9
        "4/30/2024 09:00:02 AM (CT)",
        # 10
        "1995-12-17T03:24:00",
        # 11
        "2020-05-12T23:50:21.817Z",
        # 12
        "December 17, 1995 03:24:00",
        # 13
        "2019-01-01T00:00:00.000+00:00",
    ],
)
def test_pydantic_type_date_validate_success(date_string):
    assert ParserTypeDate.validate(date_string)


@pytest.mark.parametrize(
    "date_string",
    [
        # 0
        "20/02/",  # ❌ Missing year
        # 1
        "",  # ❌ Empty string
        # 2
        "2 seconds ago",  # ❌ Time span instead of date
    ],
)
def test_pydantic_type_date_validate_error(date_string):
    with pytest.raises(ValueError):
        ParserTypeDate.validate(date_string)

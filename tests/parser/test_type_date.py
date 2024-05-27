import pytest

from harambe.parser.type_date import ParserTypeDate


@pytest.mark.parametrize(
    "date_string",
    [
        # 0
        "20/02/1991",
        # 1
        "1991-02-20",
        # 2
        "20 February, 1991",
        # 3
        "  20 February, 1991  ",
        # 4
        "  20 FEBRUARY, 1991  ",
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

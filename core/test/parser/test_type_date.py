import pytest
from datetime import datetime
from harambe_core.parser.type_date import ParserTypeDate, common_non_specific_dates


def assert_is_iso_format(date_string):
    try:
        datetime.fromisoformat(date_string)  # Validate the format
    except ValueError:
        assert False, f"Date string '{date_string}' is not in ISO 8601 format."


@pytest.mark.parametrize(
    "date_string",
    [
        "05/29/2024 02:00:00 PM",
        "5/22/2024 7:55:50 AM (EST)",
        "May 20 2024 2:00PM",
        "May 14, 2024 - 2:00pm",
        "4/30/2024 09:00:02 AM (CT)",
        "1995-12-17T03:24:00",
        "2020-05-12T23:50:21.817Z",
        "December 17, 1995 03:24:00",
        "2019-01-01T00:00:00.000+00:00",
        "2024-11-23T18:30:00",
        "11/23/24 06:30 PM",
        "November 23rd, 2024 at 6:30pm",
        "Nov 23 2024 6:30 PM (GMT+1)",
        "23rd November 2024, 18:30",
        "TBD",
        "TBA",
        "TBC",
        "Open Until Filled",
        "Open Until Contracted",
        "To Be Confirmed",
        "As Soon As Possible",
        "Subject to Change",
        "Not Specified",
        "Ongoing",
        "Continuous",
        "Pending Approval",
        "N/A",
        "Unknown",
    ],
)
def test_pydantic_type_date_validate_type_success(date_string):
    parsed_date = ParserTypeDate.validate_type(date_string)

    if date_string.lower() in common_non_specific_dates:
        assert (
            parsed_date is None
        ), f"Expected None for '{date_string}', got {parsed_date}"
    else:
        assert isinstance(
            parsed_date, str
        ), f"Expected string for '{date_string}', got {parsed_date}"
        assert_is_iso_format(parsed_date)


@pytest.mark.parametrize(
    "date_string",
    [
        # Invalid inputs
        # 0
        "",  # Empty string
        # 1
        123,  # Number instead of string
        # 2
        "InvalidDateFormat",  # Completely invalid string
        # 3
        "32/13/2024",  # Invalid date format
    ],
)
def test_pydantic_type_date_validate_type_error(date_string):
    with pytest.raises(ValueError):
        ParserTypeDate.validate_type(date_string)

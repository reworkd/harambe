import re
from datetime import datetime
from typing import Any

import dateparser
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


class ParserTypeDate:
    def __new__(cls) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type)]

    @staticmethod
    def validate_type(date: str) -> str:
        # Cast to string incase the date is a datetime float/number
        date = str(date)

        # Trim whitespaces
        date = date.strip()

        # Make sure it's not an empty string
        if len(date) == 0:
            raise ValueError("Empty input")

        # Attempt to parse date string using dateparser
        parsed_date = dateparser.parse(date)

        if parsed_date is None:
            # Remove timezone abbreviation in parentheses if present
            date = re.sub(r"\s*\(.*\)$", "", date).strip()

            # List of datetime formats to try
            datetime_formats = [
                "%m/%d/%Y %I:%M:%S %p",  # 4/30/2024 09:00:02 AM
                "%Y-%m-%dT%H:%M:%S",  # 2024-04-30T09:00:02
                "%Y-%m-%d %H:%M:%S",  # 2024-04-30 09:00:02
                "%B %d, %Y - %I:%M%p",  # May 14, 2024 - 2:00pm
                "%m/%d/%Y",  # 4/30/2024
            ]

            # Attempt to parse using datetime with specific formats
            for date_format in datetime_formats:
                try:
                    parsed_date = datetime.strptime(date, date_format)
                    break
                except ValueError:
                    continue

            if parsed_date is None:
                raise ValueError(f"Unable to parse input as date: {date}")

        # Return the date in ISO 8601 format
        return parsed_date.isoformat()

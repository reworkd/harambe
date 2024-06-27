from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

import dateparser


class ParserTypeDate:
    def __new__(self):
        return Annotated[str, AfterValidator(self.validate_type)]

    def validate_type(date: str):
        if not isinstance(date, str):
            raise ValueError("Wrong input type")

        # Trim whitespaces
        date = date.strip()

        # Make sure it's not empty string
        if len(date) == 0:
            raise ValueError("Empty input")

        # Attempt to parse date string
        try:
            dateparser.parse(date)
            return date
        except ValueError:
            pass

        raise ValueError(f"Unable to parse input as date: {date}")

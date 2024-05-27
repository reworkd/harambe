import datetime
from pydantic.functional_validators import AfterValidator
from typing import List
from typing_extensions import Annotated

date_formats: List[str] = [
    "%d/%m/%Y",  # 20/02/1991
    "%Y-%m-%d",  # 1991-02-20
    "%d %B, %Y",  # 20 February, 1991
]


class ParserTypeDate:
    def __new__(self):
        return Annotated[str, AfterValidator(self.validate)]

    def validate(date: str):
        # Trim whitespaces
        date = date.strip()

        # Make sure it's not empty string
        if len(date) == 0:
            raise ValueError("Empty input")
            return date

        # Parse date string
        for date_format in date_formats:
            try:
                datetime.datetime.strptime(date, date_format)
                return date
            except ValueError:
                pass
        raise ValueError(f"Unable to parse input as date: {date}")

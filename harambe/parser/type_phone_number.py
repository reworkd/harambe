from pydantic.functional_validators import AfterValidator
import re
from typing_extensions import Annotated

phone_number_formats = [
    r"^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$",
]


class ParserTypePhoneNumber:
    def __new__(self):
        return Annotated[str, AfterValidator(self.validate)]

    def validate(number: str) -> str:
        # Trim whitespaces
        number = number.strip()
        # Attempt to parse phone number
        for phone_number_format in phone_number_formats:
            regex = re.compile(phone_number_format)
            if regex.match(number):
                return number
        raise ValueError(f"Unable to parse input as phone number: {number}")

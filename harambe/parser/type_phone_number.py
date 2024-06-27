from pydantic.functional_validators import AfterValidator
import re
from typing_extensions import Annotated

phone_number_formats = [
    r"^\d{3,11}$",  # 911 & 11111111111
    r"^(\(?\+\d{1,2}\)?\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$",  # +1 (628) 555-3456 & (+1) 415-155-1555
    r"^\(\+\d{1,3}\)\s\d{10}(\s\(Extension:\s\d{1,4}\))?$",  # (+4) 1111111111 (Extension: 323)
    r"^(\(?\+\d{1,2}\)?\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(,\s\(?ext\.\s\d{1,4}\)?)?$",  # 206-555-7115 & 206-555-7115, ext. 239
]


class ParserTypePhoneNumber:
    def __new__(self):
        return Annotated[str, AfterValidator(self.validate_type)]

    def validate_type(number: str) -> str:
        # Trim whitespaces
        number = number.strip()
        # Attempt to parse phone number
        for phone_number_format in phone_number_formats:
            regex = re.compile(phone_number_format)
            if regex.match(number):
                return number
        raise ValueError(f"Unable to parse input as phone number: {number}")

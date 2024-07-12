import re
from typing import Type

import phonenumbers
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

phone_number_formats = [
    r"^\d{3,11}$",  # 911 & 11111111111
    r"^\d{3}[\s.-]?\d{4}$",  # 456-7890
    r"^(\(?\d{1,3}\)?[\s.-])?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$",  # +1 (628) 555-3456 & (+1) 415-155-1555
    r"^\(\d{1,3}\)\s\d{10}(\s\(Extension:\s\d{1,4}\))?$",  # (+4) 1111111111 (Extension: 323)
    r"^(\(?\d{1,3}\)?\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(,\s\(?ext\.\s\d{1,4}\)?)?$",  # 206-555-7115 & 206-555-7115, ext. 239
]


class ParserTypePhoneNumber:
    def __new__(cls) -> Type[str]:
        return Annotated[str, AfterValidator(cls.validate_type)]

    @staticmethod
    def validate_type(number: str) -> str:
        # Trim whitespaces
        formatted_number = number.strip()

        # First, try using the phonenumbers library
        try:
            phone_number = phonenumbers.parse(
                formatted_number, None
            )  # 'None' implies no specific region
            if phonenumbers.is_valid_number(phone_number):
                # Return the phone number in international format
                return phonenumbers.format_number(
                    phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
        except phonenumbers.phonenumberutil.NumberParseException:
            pass

        # If phonenumbers library fails, fall back to regex validation
        # Remove plus sign
        formatted_number = number.replace("+", "")
        # Attempt to parse phone number
        for phone_number_format in phone_number_formats:
            regex = re.compile(phone_number_format)
            if regex.match(formatted_number):
                return number
        raise ValueError(f"Unable to parse input as phone number: {number}")

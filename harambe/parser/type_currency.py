from pydantic import BeforeValidator
from typing import Any
import re
from typing_extensions import Annotated


class ParserTypeCurrency:
    def __new__(cls) -> Any:
        return Annotated[float, BeforeValidator(cls.validate_currency)]

    @staticmethod
    def validate_currency(value: str) -> float:
        # If the value is already a float, return it directly
        if isinstance(value, float):
            return value

        # Ensure the value is treated as a string
        value = str(value).strip()

        # Remove currency symbols, commas
        value = re.sub(r"[^\d.-]", "", value)
        value = value.strip()
        # Try to parse the string as a float
        try:
            parsed_value = float(value)
        except ValueError:
            raise ValueError(f"Unable to parse input as currency: {value}")

        return parsed_value

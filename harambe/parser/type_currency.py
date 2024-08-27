from pydantic import BeforeValidator
from typing import Any
import re
from typing_extensions import Annotated


class ParserTypeCurrency:
    def __new__(cls) -> Any:
        return Annotated[float, BeforeValidator(cls.validate_currency)]

    @staticmethod
    def validate_currency(value: str) -> float:
        if isinstance(value, (float, int)):
            return float(value)

        value = str(value).strip()

        if ":" in value:  # cases like 12:00
            value = re.sub(r"(?<=\d):(?=\d)", ".", value)
        cleaned_value = re.sub(r"[^\d.,-]", "", value)
        cleaned_value = re.sub(r"^0+(?!$)", "", cleaned_value)
        if "." in cleaned_value:
            decimal_parts = cleaned_value.split(".")
            if len(decimal_parts[-1]) == 2:
                cleaned_value = cleaned_value.replace(",", "")
            elif len(decimal_parts[-1]) == 3:  # thousands separators
                cleaned_value = cleaned_value.replace(".", "").replace(",", "")
        if cleaned_value.startswith("."):  # fraction
            cleaned_value = "0" + cleaned_value
            return float(cleaned_value)
        if "," in cleaned_value and "." in cleaned_value:
            cleaned_value = cleaned_value.replace(",", "")
        elif "," in cleaned_value and "." not in cleaned_value:
            cleaned_value = cleaned_value.replace(",", "")
        cleaned_value = cleaned_value.strip()

        parsed_value = float(cleaned_value)

        return parsed_value

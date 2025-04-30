import re
from typing import Any

from pydantic import BeforeValidator
from typing_extensions import Annotated, deprecated

from harambe_core.parser.constants import PRICE_NOT_AVAILABLE_PHRASES


@deprecated("Use ParserTypePrice instead, this is deprecated pending removal")
class ParserTypeCurrency:
    def __new__(cls) -> Any:
        return Annotated[float | None, BeforeValidator(cls.validate_currency)]

    @staticmethod
    def validate_currency(value: str) -> float | None:
        if isinstance(value, (float, int)):
            return float(value)

        value = str(value).strip()

        if value.lower() in PRICE_NOT_AVAILABLE_PHRASES:
            return None

        cleaned_value = re.sub(r"[^\d.,-]", "", value)
        cleaned_value = re.sub(r"^0+(?!$)", "", cleaned_value)

        if "." in cleaned_value:
            decimal_parts = cleaned_value.split(".")
            if len(decimal_parts[-1]) == 3:  # thousands separator issue
                cleaned_value = cleaned_value.replace(".", "")

        if cleaned_value.startswith("."):
            cleaned_value = "0" + cleaned_value
            return float(cleaned_value)

        if "," in cleaned_value and "." in cleaned_value:
            if cleaned_value.index(",") < cleaned_value.index("."):
                cleaned_value = cleaned_value.replace(",", "")
            else:
                cleaned_value = cleaned_value.replace(".", "").replace(",", ".")
        elif "," in cleaned_value and "." not in cleaned_value:
            if len(cleaned_value.split(",")[-1]) == 2:
                cleaned_value = cleaned_value.replace(",", ".")

            elif (
                len(cleaned_value.split(",")[-1]) != 3
            ):  # check Ambiguous values 123,45 and 123,456
                raise ValueError("Invalid price")
            cleaned_value = cleaned_value.replace(",", "")

        return float(cleaned_value.strip())

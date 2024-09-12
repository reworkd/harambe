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
        cleaned_value = re.sub(r"[^\d.,-]", "", value)
        cleaned_value = re.sub(r"^0+(?!$)", "", cleaned_value)

        if "." in cleaned_value:
            decimal_parts = cleaned_value.split(".")
            if len(decimal_parts[-1]) == 3:  # thousands separators
                cleaned_value = cleaned_value.replace(".", "")

        if cleaned_value.startswith("."):  # fraction
            cleaned_value = "0" + cleaned_value
            return float(cleaned_value)

        if "," in cleaned_value and "." in cleaned_value:
            if cleaned_value.index(",") < cleaned_value.index("."):
                cleaned_value = cleaned_value.replace(",", "")
            else:
                cleaned_value = cleaned_value.replace(".", "").replace(",", ".")
        elif "," in cleaned_value and "." not in cleaned_value:
            if (
                len(cleaned_value.split(",")[-1].split(".")[0]) != 3
            ):  # check Ambiguous values 123,45 and 123,456,12
                raise ValueError("Can not convert to float")
            cleaned_value = cleaned_value.replace(",", "")
        value = value.strip()

        parsed_value = float(cleaned_value)

        return parsed_value

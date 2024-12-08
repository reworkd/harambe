from pydantic import BeforeValidator
from typing import Any, Union
import re
from typing_extensions import Annotated


class ParserTypePrice:
    def __new__(cls) -> Any:
        return Annotated[Union[float, None], BeforeValidator(cls.validate_price)]

    @staticmethod
    def validate_price(value: str) -> Union[float, None]:
        value = str(value).strip()

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
            if (
                len(cleaned_value.split(",")[-1]) != 3
            ):  # check Ambiguous values 123,45 and 123,456
                raise ValueError("Invalid price")
            cleaned_value = cleaned_value.replace(",", "")

        return float(cleaned_value.strip())

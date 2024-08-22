from pydantic import BeforeValidator
from typing import Any
import re
from typing_extensions import Annotated


class ParserTypeCurrency:
    def __new__(cls) -> Any:
        return Annotated[float, BeforeValidator(cls.validate_currency)]

    @staticmethod
    def validate_currency(value: str) -> float:
        if isinstance(value, float):
            return value

        value = str(value).strip()

        value = re.sub(r"[^\d.-]", "", value)
        value = value.strip()

        parsed_value = float(value)

        return parsed_value

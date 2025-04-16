from typing import Any, Callable

from pydantic import BeforeValidator
from typing_extensions import Annotated, Literal


class ParserTypeEnum:
    def __new__(cls, *variants: str, required: bool = True) -> Any:
        validator = BeforeValidator(cls.validate_type(*variants, required=required))
        base = Literal[*variants] if required else Literal[*variants] | None

        return Annotated[base, validator]

    @staticmethod
    def validate_type(*variants: str, required: bool) -> Callable[[str], str]:
        variant_map = {v.strip().lower(): v for v in variants}

        def _validate_type(value: str | None) -> str | None:
            if not isinstance(value, str):
                return value

            if (value := value.strip().lower()) not in variant_map:
                return value

            return variant_map[value]

        return _validate_type

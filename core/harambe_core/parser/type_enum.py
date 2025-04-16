from typing import Any, Callable

from pydantic import BeforeValidator
from typing_extensions import Annotated, Literal


class ParserTypeEnum:
    def __new__(cls, *variants: str, required: bool = True) -> Any:
        validator = BeforeValidator(cls.validate_type(*variants))
        base = Literal[*variants] if required else Literal[*variants] | None

        return Annotated[base, validator]

    @staticmethod
    def validate_type(*variants: str) -> Callable[[Any], str]:
        variant_map = {v.strip().lower(): v for v in variants}

        def _validate_type(value: Any) -> Any:
            if not isinstance(value, str):
                return value

            if (value := value.strip().lower()) not in variant_map:
                return value

            return variant_map[value]

        return _validate_type

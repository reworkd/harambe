from typing import Any, List

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


class ParserTypeEnum:
    def __new__(cls, variants: list[str]) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type(variants))]

    @staticmethod
    def validate_type(variants: list[str]) -> Any:
        def _validate_type(value: str) -> str:
            # Check if the value exists among variants
            if value not in variants:
                raise ValueError(
                    f'Value "{value}" doesn\'t match any of the variants ({variants})'
                )
            return value

        return _validate_type

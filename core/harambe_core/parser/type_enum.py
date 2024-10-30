from typing import Any, List

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from harambe.types import Enum


class ParserTypeEnum:
    def __new__(cls, variants: List[Enum]) -> Any:
        return Annotated[Enum, AfterValidator(cls.validate_type(variants))]

    @staticmethod
    def validate_type(variants: List[Enum]) -> Any:
        def _validate_type(value: Enum) -> Enum:
            # Check if the value exists among variants
            if value not in variants:
                raise ValueError(
                    f'Value "{value}" doesn\'t match any of the variants ({variants})'
                )
            return value

        return _validate_type

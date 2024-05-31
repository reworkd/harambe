from pydantic.functional_validators import AfterValidator
from typing import List
from typing_extensions import Annotated

from harambe.types import Enum


class ParserTypeEnum:
    def __new__(self, variants: List[Enum]):
        return Annotated[Enum, AfterValidator(self.validate(variants))]

    def validate(variants: List[Enum]):
        def _validate(value: Enum) -> Enum:
            # Check if the value exists among variants
            if value not in variants:
                raise ValueError(
                    f'Value "{value}" doesn\'t match any of the variants ({variants})'
                )
            return value

        return _validate
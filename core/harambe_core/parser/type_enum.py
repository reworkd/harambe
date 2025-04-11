from typing import Any, List, Callable

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


class ParserTypeEnum:
    def __new__(cls, *variants: str) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type(*variants))]

    @staticmethod
    def validate_type(*variants: str) -> Callable[[str], str]:
        variant_map = {v.strip().lower(): v for v in variants}

        def _validate_type(value: str) -> str:
            if (value := value.strip().lower()) not in variant_map:
                raise ValueError(
                    f'Value "{value}" doesn\'t match any of the variants ({variants})'
                )

            return variant_map[value]

        return _validate_type

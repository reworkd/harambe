from typing import Annotated

from pydantic import BeforeValidator

ParserTypeNumber = Annotated[
    float,
    BeforeValidator(
        lambda value: value.replace(",", "") if isinstance(value, str) else value
    ),
]

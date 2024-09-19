from typing import Annotated

from pydantic import BeforeValidator, validate_email


def _validate_email(value: str) -> str:
    if isinstance(value, str):
        value = value.strip().lower().removeprefix("mailto:")
        return validate_email(value)[1]
    return value


ParserTypeEmail = Annotated[
    str,
    BeforeValidator(_validate_email),
]

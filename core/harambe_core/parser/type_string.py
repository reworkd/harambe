from typing import Annotated

from pydantic import AfterValidator

ParserTypeString = Annotated[
    str,
    AfterValidator(lambda value: value if value else None),
]

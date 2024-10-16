from typing import Any, Callable, Optional

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from harambe.normalize_url import normalize_url
from harambe.types import URL


class ParserTypeUrl:
    def __new__(cls, base_url: Optional[URL] = None) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type(base_url))]

    @staticmethod
    def validate_type(base_url: Optional[URL]) -> Callable[[URL], str]:
        def _validate_type(url: URL) -> str:
            return normalize_url(url, base_url)

        return _validate_type

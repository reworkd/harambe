from typing import Any, Callable, Optional

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from harambe_core.normalize_url import normalize_url


class ParserTypeUrl:
    def __new__(cls, base_url: Optional[str] = None) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type(base_url))]

    @staticmethod
    def validate_type(base_url: Optional[str]) -> Callable[[str], str]:
        def _validate_type(url: str) -> str:
            url = normalize_url(url, base_url)
            ParserTypeUrl._validate_tld(url)
            return url

        return _validate_type

    @staticmethod
    def _validate_tld(url: str) -> None:
        domain = url.split(".")
        if len(domain) < 2:
            raise ValueError(f"Url does not have a valid TLD")

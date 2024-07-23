from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse

from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from harambe.types import URL

allowed_url_schemes = [
    "data",
    "file",
    "http",
    "https",
    "mailto",
    "s3",
]


class ParserTypeUrl:
    def __new__(cls, base_url: Optional[URL] = None) -> Any:
        return Annotated[str, AfterValidator(cls.validate_type(base_url))]

    @staticmethod
    def validate_type(base_url: Optional[URL]) -> Callable[[URL], str]:
        def _validate_type(url: URL) -> str:
            # Transform relative URLs into absolute using base_url
            if base_url is not None:
                parsed_base_url = urlparse(base_url, allow_fragments=False)
                url = urljoin(parsed_base_url.geturl(), url)

            # Parse the URL
            try:
                parsed_url = urlparse(url)
            except ValueError as e:
                raise ValueError(f"Unable to parse URL: {url}", e)

            # Check if the scheme is allowed
            if parsed_url.scheme not in allowed_url_schemes:
                raise ValueError(f"Invalid URL scheme: {url}")

            return url

        return _validate_type

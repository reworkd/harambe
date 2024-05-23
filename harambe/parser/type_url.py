from pydantic.functional_validators import AfterValidator
from typing import Optional
from typing_extensions import Annotated
import urllib.parse

from harambe.types import URL
from harambe.normalize_url import normalize_url

allowed_url_schemes = [
    "data",
    "file",
    "http",
    "https",
    "mailto",
    "s3",
]


class ParserTypeUrl:
    def __new__(self, base_url: Optional[URL] = None):
        return Annotated[URL, AfterValidator(self.validate_url(base_url))]

    def validate_url(base_url: Optional[URL]):
        def _validate_url(url: URL) -> str:
            # Transform relative URLs into absolute using base_url
            if base_url is not None:
                url = normalize_url(url, base_path=base_url)

            # Parse the URL
            try:
                parsed_url = urllib.parse.urlparse(url)
            except ValueError as e:
                raise ValueError(f"Unable to parse URL: {url}", e)

            # Check if the scheme is allowed
            if parsed_url.scheme not in allowed_url_schemes:
                raise ValueError(f"Invalid URL: {url}")

            return url

        return _validate_url

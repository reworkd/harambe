from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
import urllib.parse

from harambe.types import URL

allowed_url_schemes = [
    "data",
    "file",
    "http",
    "https",
    "mailto",
    "s3",
]


def validate_url(url: URL) -> str:
    # Allow empty URLs
    if url == "":
        return url

    # Parse the URL
    try:
        parsed_url = urllib.parse.urlparse(url)
    except ValueError as e:
        raise ValueError(f"Unable to parse URL: {url}", e)

    # Check if the scheme is allowed
    if parsed_url.scheme not in allowed_url_schemes:
        raise ValueError(f"Invalid URL: {url}")

    return url


ParserTypeUrl = Annotated[URL, AfterValidator(validate_url)]

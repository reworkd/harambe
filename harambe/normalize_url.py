from urllib.parse import urljoin, urlparse, urlunparse


def normalize_url(path: str, base_path: str | None) -> str:
    """
    Normalizes an absolute or relative URL path based on the provided base URL.

    :param base_path: The base URL from which the path was scraped.
    :param path: The absolute or relative path to be normalized.
    :return: Normalized URL.
    """
    path = sanitize_scheme(path)
    validate_allowed_scheme(path)
    path = _normalize(path)
    escaped_path = path.replace(" ", "%20")

    if base_path is None:
        return escaped_path

    validate_allowed_scheme(base_path, scheme_required=True)

    parsed_base_url = urlparse(base_path, allow_fragments=False)
    return urljoin(parsed_base_url.geturl(), escaped_path)


def _normalize(url: str) -> str:
    parsed_url = urlparse(url)
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc.replace("\\", "/"),
            parsed_url.path.replace("\\", "/").replace("//", "/"),
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )


def sanitize_scheme(url: str) -> str:
    last_scheme_index = find_highest_index_before_period(url, "/")
    base = "https://"
    if url.startswith("http:"):
        base = "http://"
    return base + url[last_scheme_index + 1 :] if last_scheme_index > 0 else url


allowed_url_schemes = ["http", "https", "s3", "file"]


def validate_allowed_scheme(url: str, scheme_required: bool = False) -> None:
    scheme = urlparse(url).scheme
    if (scheme_required and not scheme) or (
        scheme and scheme not in allowed_url_schemes
    ):
        raise ValueError(f"URL scheme {scheme} not allowed.")


def find_highest_index_before_period(s: str, char: str) -> int:
    """
    Find the highest index of a specified character before the first period in a string.

    :param s: The string to search.
    :param char: The character to find.
    :return: The highest index of the character before the first period, or -1
    """
    if not s.startswith("http:") and not s.startswith("https:"):
        return -1

    highest_index = -1
    for i, c in enumerate(s):
        if c == ".":
            break
        if c == char:
            highest_index = i
    return highest_index

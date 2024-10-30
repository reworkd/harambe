import pytest

from harambe_core.parser.type_url import ParserTypeUrl


@pytest.mark.parametrize(
    "url, base_url_, expected",
    [
        (
            "",
            "http://example.com",
            "http://example.com",
        ),
        (
            "",
            "https://www.example.com",
            "https://www.example.com",
        ),
        (
            "/",
            "http://example.com",
            "http://example.com/",
        ),
        (
            "/doc6",
            "http://www.example.com",
            "http://www.example.com/doc6",
        ),
        (
            "#",
            "http://example.com",
            "http://example.com",
        ),
        (
            "#fragment",
            "http://example.com",
            "http://example.com#fragment",
        ),
        (
            "https://www.example.com",
            "https://subdomain.example.com",
            "https://www.example.com",
        ),
        (
            "",
            "s3://bucket-name/file-name.pdf",
            "s3://bucket-name/file-name.pdf",
        ),
        (
            "s3://bucket-name/file-name.pdf",
            "https://www.example.com",
            "s3://bucket-name/file-name.pdf",
        ),
        (
            "https://www.example.com",
            "s3://bucket-name/file-name.pdf",
            "https://www.example.com",
        ),
        (
            "//example.com/doc1",
            "https://example.com",
            "https://example.com/doc1",
        ),
    ],
)
def test_pydantic_type_url_validate_type_success(url, base_url_, expected):
    assert ParserTypeUrl.validate_type(base_url_)(url) == expected


@pytest.mark.parametrize(
    "url, base_url_",
    [
        (
            "",
            "",  # ❌ An empty string
        ),
        (
            "",
            "www.example.com",  # ❌ Isn't a valid URL
        ),
        (
            "",
            "s4://bucket-name/file-name.pdf",  # ❌ Bad URL scheme
        ),
        (
            "htp://example.com/doc1",  # ❌ Bad URL scheme
            "https://example.com",
        ),
        (
            "mailto:info@example.com",
            "https://example.com",
        ),
    ],
)
def test_pydantic_type_url_validate_type_error(url, base_url_):
    with pytest.raises(ValueError):
        ParserTypeUrl.validate_type(base_url_)(url)

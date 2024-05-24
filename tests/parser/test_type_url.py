import pytest

from harambe.parser.type_url import ParserTypeUrl


@pytest.mark.parametrize(
    "url, base_url, expected",
    [
        # 0
        (
            # url
            "",
            # base_url
            "http://example.com",
            # expected
            "http://example.com",
        ),
        # 1
        (
            # url
            "",
            # base_url
            "https://www.example.com",
            # expected
            "https://www.example.com",
        ),
        # 2
        (
            # url
            "/",
            # base_url
            "http://example.com",
            # expected
            "http://example.com/",
        ),
        # 3
        (
            # url
            "/doc6",
            # base_url
            "http://www.example.com",
            # expected
            "http://www.example.com/doc6",
        ),
        # 4
        (
            # url
            "#",
            # base_url
            "http://example.com",
            # expected
            "http://example.com",
        ),
        # 5
        (
            # url
            "#fragment",
            # base_url
            "http://example.com",
            # expected
            "http://example.com#fragment",
        ),
        # 6
        (
            # url
            "https://www.example.com",
            # base_url
            "https://subdomain.example.com",
            # expected
            "https://www.example.com",
        ),
        # 7
        (
            # url
            "",
            # base_url
            "s3://bucket-name/file-name.pdf",
            # expected
            "s3://bucket-name/file-name.pdf",
        ),
        # 8
        (
            # url
            "s3://bucket-name/file-name.pdf",
            # base_url
            "https://www.example.com",
            # expected
            "s3://bucket-name/file-name.pdf",
        ),
        # 9
        (
            # url
            "https://www.example.com",
            # base_url
            "s3://bucket-name/file-name.pdf",
            # expected
            "https://www.example.com",
        ),
        # 10
        (
            # url
            "mailto:info@example.com",
            # base_url
            "https://www.example.com",
            # expected
            "mailto:info@example.com",
        ),
    ],
)
def test_pydantic_type_url_validate_url_success(url, base_url, expected):
    assert ParserTypeUrl.validate_url(base_url)(url) == expected


@pytest.mark.parametrize(
    "url, base_url, expected",
    [
        # 0
        (
            # url
            "",
            # base_url
            "",  # ❌ An empty string
            # expected
            "",
        ),
        # 1
        (
            # url
            "",
            # base_url
            "www.example.com",  # ❌ Isn't a valid URL
            # expected
            "",
        ),
        # 2
        (
            # url
            "",
            # base_url
            "s4://bucket-name/file-name.pdf",  # ❌ Bad URL scheme
            # expected
            "",
        ),
    ],
)
def test_pydantic_type_url_validate_url_error(url, base_url, expected):
    with pytest.raises(ValueError):
        ParserTypeUrl.validate_url(base_url)(url) == expected

import ast
from pathlib import Path

import pytest

from harambe import SDK, meta


@SDK.scraper(domain="com.example", stage="listing")
async def example_scraper(sdk: SDK):
    pass


def test_find_scrapers():
    scrapers = meta.walk_package_for_decorators(Path(__file__))
    assert len(scrapers) == 1

    for scraper in scrapers:
        assert scraper["domain"]
        assert scraper["stage"]
        assert scraper["file_path"]
        assert scraper["function_name"]
        assert scraper["package"] == meta.url_to_package(scraper["domain"])


@pytest.mark.parametrize(
    "url, expected",
    [
        ("www.example.com", "com.example"),
        ("http://example.com", "com.example"),
        ("https://www.example.com", "com.example"),
        ("https://subdomain.example.com", "com.example.subdomain"),
        ("http://example.co.uk", "uk.co.example"),
    ],
)
def test_url_to_package(url, expected):
    assert meta.url_to_package(url) == expected


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://example.com", "example.com"),
        ("https://example.com", "example.com"),
        ("example.com", "example.com"),
        ("www.example.com", "example.com"),
        ("subdomain.example.com", "subdomain.example.com"),
        ("example.com:8000", "example.com"),
    ],
)
def test_url_to_netloc(url, expected):
    assert meta.url_to_netloc(url) == expected


@pytest.mark.parametrize(
    "node, expected",
    [
        (ast.Call(func=ast.Attribute(value=ast.Name(id="SDK"), attr="scraper")), True),
        (
            ast.Call(func=ast.Attribute(value=ast.Name(id="NotSDK"), attr="scraper")),
            False,
        ),
        (
            ast.Call(func=ast.Attribute(value=ast.Name(id="SDK"), attr="not_scraper")),
            False,
        ),
        (ast.Call(func=ast.Attribute(value=ast.Num(n=123), attr="scraper")), False),
        (ast.Num(n=123), False),
    ],
)
def test_is_sdk_scraper_decorator(node, expected):
    assert meta.is_sdk_scraper_decorator(node) == expected

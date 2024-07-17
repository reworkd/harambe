import pytest

from harambe.contrib import playwright_harness, soup_harness, WebHarness


@pytest.fixture(params=[playwright_harness, soup_harness])
def web_harness(request) -> WebHarness:
    return request.param


async def test_with_cookies(web_harness):
    async with web_harness(
        cookies=[
            {"url": "https://example.com", "name": "foo", "value": "bar"},
            {
                "url": "https://example.com",
                "name": "baz",
                "value": "qux",
            },
        ]
    ) as page_factory:
        assert page_factory

import pytest

from harambe.contrib import WebHarness, playwright_harness, soup_harness


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


async def test_with_user_agent():
    async with playwright_harness(user_agent=lambda: "my-user-agent") as page_factory:
        page = await page_factory()
        user_agent = await page.evaluate("navigator.userAgent")
        assert user_agent == "my-user-agent"


async def test_default_url(web_harness):
    async with web_harness() as page_factory:
        page = await page_factory()
        assert page.url == "about:blank"

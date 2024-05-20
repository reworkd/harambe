from unittest.mock import AsyncMock, call

import pytest
from playwright.async_api import Page

from harambe.core import SDK, URL, AsyncScraperType, Context
from harambe.observer import OutputObserver


@pytest.fixture
def scraper() -> AsyncScraperType:
    async def dummy_scraper(sdk: "SDK", url: URL, context: Context) -> None:
        await sdk.page.goto(url)
        await sdk.enqueue("/test", context={"foo": "bar"})
        await sdk.save_data({"baz": "qux"})

    return dummy_scraper


def test_sdk_init_assigns_correct_values():
    page = AsyncMock(spec=Page)
    run_id = "test_run_id"
    observer = AsyncMock(spec=OutputObserver)

    sdk = SDK(page, run_id, "test_domain", "listing", observer)

    assert sdk.page == page
    assert sdk._id == run_id
    assert sdk._domain == "test_domain"
    assert sdk._stage == "listing"
    assert sdk._observers == [observer]


@pytest.mark.asyncio
async def test_sdk_save_data_calls_on_save_data_for_each_observer():
    page = AsyncMock(spec=Page)
    observer = AsyncMock(spec=OutputObserver)
    sdk = SDK(page, observer=observer)
    data = [{"foo": "bar"}, {"baz": "qux"}]

    await sdk.save_data(*data)
    assert observer.on_save_data.call_count == len(data)


@pytest.mark.asyncio
async def test_sdk_enqueue_calls_on_enqueue_url_for_each_observer():
    page = AsyncMock(spec=Page)
    page.url = "https://example.net"
    observer = AsyncMock(spec=OutputObserver)
    sdk = SDK(page, observer=observer)
    urls = ["https://example.org", "https://example.com"]
    context = {"foo": "bar"}

    await sdk.enqueue(*urls, context=context)

    assert observer.on_queue_url.call_count == len(urls)
    observer.on_queue_url.assert_has_awaits(
        [call(urls[0], context), call(urls[1], context)], any_order=False
    )

    assert observer.on_queue_url.call_count == len(urls)
    observer.on_save_data.assert_not_awaited()


# noinspection PyUnresolvedReferences
def test_scraper_decorator_adds_domain_and_stage_to_function(scraper):
    decorated_scraper = SDK.scraper("https://example.org", "listing")(scraper)

    assert decorated_scraper.domain == "https://example.org"
    assert decorated_scraper.stage == "listing"


# noinspection PyUnresolvedReferences
def test_scraper_decorator_adds_observers_to_function(scraper):
    domain = "https://example.org"

    decorated_scraper = SDK.scraper(domain, "detail")(scraper)
    assert len(decorated_scraper.observer) == 2


@pytest.mark.asyncio
async def test_scraper_decorator_preserves_functionality_of_decorated_function(scraper):
    decorated_scraper = SDK.scraper("https://example.org", "listing")(scraper)

    sdk = AsyncMock(spec=SDK)
    sdk.page = AsyncMock()

    url = "https://example.org"
    context = {}

    await decorated_scraper(sdk, url, context)

    sdk.page.goto.assert_awaited_once_with(url)
    sdk.enqueue.assert_awaited_once_with("/test", context={"foo": "bar"})
    sdk.save_data.assert_awaited_once_with({"baz": "qux"})

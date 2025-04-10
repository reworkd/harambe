from unittest.mock import AsyncMock, call

import pytest
from playwright.async_api import Page

from harambe.core import SDK, URL, AsyncScraperType, Context
from harambe_core import Schema
from harambe_core.errors import SchemaValidationError
from harambe_core.observer import OutputObserver


@pytest.fixture
def scraper() -> AsyncScraperType:
    async def dummy_scraper(sdk: "SDK", url: URL, context: Context) -> None:
        await sdk.page.goto(url)
        await sdk.enqueue("/test", context={"foo": "bar"})
        await sdk.save_data({"baz": "qux"})

    return dummy_scraper


@pytest.fixture
def page(mocker):
    mock_page = mocker.AsyncMock(spec=Page)
    mock_page.url = "https://example.com"
    mock_page.query_selector = mocker.AsyncMock(return_value=None)
    return mock_page


def test_sdk_init_assigns_correct_values(page):
    run_id = "test_run_id"
    observer = AsyncMock(spec=OutputObserver)

    sdk = SDK(page, run_id, "test_domain", "listing", observer)

    assert sdk.page == page
    assert sdk._id == run_id
    assert sdk._domain == "test_domain"
    assert sdk._stage == "listing"
    assert sdk._observers == [observer]


async def test_sdk_save_data_calls_on_save_data_for_each_observer(page):
    observer = AsyncMock(spec=OutputObserver)
    sdk = SDK(page, observer=observer)
    data = [{"foo": "bar"}, {"baz": "qux"}]

    await sdk.save_data(*data)
    assert observer.on_save_data.call_count == len(data)


async def test_sdk_enqueue_calls_on_enqueue_url_for_each_observer(page):
    observer = AsyncMock(spec=OutputObserver)
    sdk = SDK(page, observer=observer)
    urls = ["https://example.org", "https://example.com"]
    context = {"foo": "bar"}
    options = {"zoo": "zar"}

    await sdk.enqueue(*urls, context=context, options=options)

    assert observer.on_queue_url.await_count == len(urls)
    observer.on_queue_url.assert_has_awaits(
        [call(urls[0], context, options), call(urls[1], context, options)],
        any_order=False,
    )

    observer.on_save_data.assert_not_awaited()
    page.query_selector.assert_awaited_once_with("base")


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


async def test_sdk_save_data_saves_valid_data(page):
    page.url = "https://example.net"
    observer = AsyncMock(spec=OutputObserver)
    schema: Schema = {
        "name": {"type": "string", "description": "The name of the person"},
        "age": {
            "type": "integer",
            "description": "Person's age",
        },
        "url": {
            "type": "url",
            "description": "Person's website",
        },
    }
    sdk = SDK(page, observer=observer, schema=schema)
    data = [
        {"name": "Joe Doe", "age": None, "url": "https://example.com"},
        {"name": "Jane Doe", "age": 33, "url": None},
    ]

    await sdk.save_data(*data)
    assert observer.on_save_data.call_count == 2


async def test_sdk_save_data_does_not_save_invalid_data(page):
    observer = AsyncMock(spec=OutputObserver)
    schema: Schema = {"foo": {"type": "string", "description": "Something something"}}
    sdk = SDK(page, observer=observer, schema=schema)
    data = [{"baz": "456"}]

    with pytest.raises(SchemaValidationError):
        await sdk.save_data(*data)

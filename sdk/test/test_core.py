from unittest.mock import call

from harambe import SDK
from harambe.contrib.soup.impl import SoupPage


async def test_enqueue(mocker):
    page = mocker.AsyncMock(spec=SoupPage)
    page.url = "https://example.com"
    query_selector = mocker.AsyncMock(return_value=None)
    page.query_selector = query_selector

    observer = mocker.AsyncMock()

    sdk = SDK(page=page, observer=observer)

    await sdk.enqueue("https://example.com")
    await sdk.enqueue("https://example.ca")

    query_selector.assert_awaited_once_with("base")

    assert observer.on_queue_url.await_count == 2
    observer.on_queue_url.assert_has_awaits(
        [
            call("https://example.com", {"__url": "https://example.com"}, {}),
            call("https://example.ca", {"__url": "https://example.com"}, {}),
        ]
    )

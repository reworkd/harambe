import datetime
from unittest.mock import AsyncMock

import pytest

from harambe.core import SDK
from harambe.instrumentation import HarambeInstrumentation, SdkCall


class InMemorySink(HarambeInstrumentation):

    def __init__(self) -> None:
        self.events = []

    def sink(self, event: SdkCall) -> None:
        self.events.append(event)


@pytest.fixture(autouse=True)
def patch_perf_counter_and_datetime(mocker):
    mocker.patch("harambe.instrumentation.perf_counter", side_effect=[0.0, 1.0])
    dt = mocker.patch("harambe.instrumentation.datetime")
    dt.now.return_value = datetime.datetime(1997, 3, 8)


@pytest.fixture
def sdk(mocker):
    page = mocker.Mock()
    page.query_selector = AsyncMock(return_value=None)
    page.url = "https://example.com"
    return SDK(page=page)


@pytest.fixture
def instrumentation() -> InMemorySink:
    return InMemorySink()


async def test_successful_method_call(sdk, instrumentation):
    instrumentation.instrument(sdk)
    await sdk.save_data({"test": "data"})

    assert len(instrumentation.events) == 1
    event = instrumentation.events[0]
    assert event["method"] == "save_data"
    assert event["args"] == ["{'test': 'data'}"]
    assert event["kwargs"] == {}
    assert event["result"] == 'None'
    assert event['timestamp'] == 857808000.0
    assert event["execution_time"] == 1.0


async def test_method_call_with_exception(sdk, instrumentation):
    instrumentation.instrument(sdk)
    with pytest.raises(ValueError) as e:
        await sdk.capture_html("div.content")

    # Verify the event was recorded
    assert len(instrumentation.events) == 1
    event = instrumentation.events[0]
    assert event["method"] == "capture_html"
    assert event["args"] == ["'div.content'"]
    assert event["kwargs"] == {}
    assert event["result"] == "ValueError('Element not found for selector: div.content')"
    assert event['timestamp'] == 857808000.0
    assert event["execution_time"] == 1.0


async def test_method_call_with_return_value(sdk, instrumentation, mocker):
    sdk.page.wait_for_timeout = AsyncMock()
    sdk.page.pdf = AsyncMock(return_value=b"pdf")

    instrumentation.instrument(sdk)
    result = await sdk.capture_pdf()

    expected_result = {'url': 'https://example.com/reworkd_page_pdf.pdf', 'filename': 'reworkd_page_pdf.pdf'}
    assert result == expected_result

    assert len(instrumentation.events) == 1
    event = instrumentation.events[0]

    assert event["method"] == "capture_pdf"
    assert event["args"] == []
    assert event["kwargs"] == {}
    assert event["result"] == str(expected_result)
    assert event['timestamp'] == 857808000.0


async def test_method_with_args_and_kwargs(sdk, instrumentation):
    instrumentation.instrument(sdk)
    await sdk.enqueue("https://example.com", "https://example.com/next", options={"waitUntil": "load"},
                      context={"foo": "bar"})

    assert len(instrumentation.events) == 1
    event = instrumentation.events[0]
    assert event["method"] == "enqueue"
    assert event["args"] == ["'https://example.com'", "'https://example.com/next'"]
    assert event["kwargs"] == {'context': "{'foo': 'bar'}", 'options': "{'waitUntil': 'load'}"}
    assert event["result"] == 'None'
    assert event['timestamp'] == 857808000.0
    assert event["execution_time"] == 1.0

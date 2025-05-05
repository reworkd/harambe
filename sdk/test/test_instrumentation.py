import datetime
from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Page

from harambe.contrib.soup.impl import SoupPage
from harambe.core import SDK
from harambe.instrumentation import HarambeInstrumentation, InMemoryExporter


@pytest.fixture(autouse=True)
def patch_perf_counter_and_datetime(mocker):
    mocker.patch("harambe.instrumentation.perf_counter", side_effect=[0.0, 1.0] * 100)
    dt = mocker.patch("harambe.instrumentation.datetime")
    dt.now.return_value = datetime.datetime(1997, 3, 8, tzinfo=datetime.UTC)


@pytest.fixture
def exporter():
    return InMemoryExporter()


@pytest.fixture(
    params=[
        Page(
            impl_obj=AsyncMock(
                url="https://example.com", query_selector=AsyncMock(return_value=None)
            )
        ),
        SoupPage(session=AsyncMock(), url="https://example.com"),
    ]
)
def sdk(request, exporter):
    instrumentation = (
        HarambeInstrumentation().add_exporter(exporter.export).instrument()
    )
    yield SDK(page=request.param)
    instrumentation.un_instrument()


async def test_successful_method_call(sdk, exporter):
    await sdk.save_data({"test": "data"})

    assert len(exporter.events) == 2
    event = exporter.events[0]

    page_cls = sdk.page.__class__.__name__
    assert event["method"] == f"{page_cls}.query_selector"
    assert event["args"] == ["base"]
    assert event["kwargs"] == {}
    assert event["result"] == "None"
    assert event["timestamp"] == 857779200.0

    event = exporter.events[1]
    assert event["method"] == "SDK.save_data"
    assert event["args"] == ["{'test': 'data'}"]
    assert event["kwargs"] == {}
    assert event["result"] == "None"
    assert event["timestamp"] == 857779200.0
    assert event["execution_time"] == 1.0


async def test_method_call_with_exception(sdk, exporter):
    with pytest.raises(ValueError) as e:
        await sdk.capture_html("div.content")

    # Verify the event was recorded
    assert len(exporter.events) == 2
    page_cls = sdk.page.__class__.__name__
    assert exporter.events[0]["method"] == f"{page_cls}.query_selector"
    assert exporter.events[0]["result"] == "None"

    event = exporter.events[1]
    assert event["method"] == "SDK.capture_html"
    assert event["args"] == ["div.content"]
    assert event["kwargs"] == {}
    assert (
        event["result"] == "ValueError('Element not found for selector: div.content')"
    )
    assert event["timestamp"] == 857779200.0
    assert event["execution_time"] == 1.0


async def test_method_call_with_return_value(sdk, exporter):
    sdk.page.pdf = AsyncMock(return_value=b"pdf")

    result = await sdk.capture_pdf()

    expected_result = {
        "url": "https://example.com/reworkd_page_pdf.pdf",
        "filename": "reworkd_page_pdf.pdf",
        "path": "",
    }
    assert result == expected_result

    event = exporter.events[-1]
    assert event["method"] == "SDK.capture_pdf"
    assert event["args"] == []
    assert event["kwargs"] == {}
    assert event["result"] == str(expected_result)
    assert event["timestamp"] == 857779200.0


async def test_method_with_args_and_kwargs(sdk, exporter):
    await sdk.enqueue(
        "https://example.com",
        "https://example.com/next",
        options={"waitUntil": "load"},
        context={"foo": "bar"},
    )

    assert len(exporter.events) == 2
    page_cls = sdk.page.__class__.__name__
    assert exporter.events[0]["method"] == f"{page_cls}.query_selector"

    event = exporter.events[1]
    assert event["method"] == "SDK.enqueue"
    assert event["args"] == ["https://example.com", "https://example.com/next"]
    assert event["kwargs"] == {
        "context": "{'foo': 'bar'}",
        "options": "{'waitUntil': 'load'}",
    }
    assert event["result"] == "None"
    assert event["timestamp"] == 857779200.0
    assert event["execution_time"] == 1.0

import pytest

from harambe.observer import InMemoryObserver, StopPaginationObserver


@pytest.mark.asyncio
async def in_memory_on_save_data():
    observer = InMemoryObserver()

    await observer.on_save_data({"foo": "bar"})
    await observer.on_save_data({"baz": "qux"})

    assert observer.data == [{"foo": "bar"}, {"baz": "qux"}]


@pytest.mark.asyncio
async def in_memory_on_queue_url():
    observer = InMemoryObserver()

    await observer.on_queue_url("https://example.com", {"foo": "bar"})
    await observer.on_queue_url("https://example.org", {"baz": "qux"})

    assert observer.urls == [
        ("https://example.com", {"foo": "bar"}),
        ("https://example.org", {"baz": "qux"}),
    ]


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_data_error():
    observer = StopPaginationObserver()

    await observer.on_save_data({"foo": "bar"})
    observer.on_paginate("https://example.com/page2")

    with pytest.raises(StopAsyncIteration):
        await observer.on_save_data({"foo": "bar"})


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_url_error():
    observer = StopPaginationObserver()

    await observer.on_queue_url("https://example.com", {"foo": "bar"})
    observer.on_paginate("https://example.com/page2")

    with pytest.raises(StopAsyncIteration):
        await observer.on_queue_url("https://example.com", {"foo": "bar"})


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_download_error():
    observer = StopPaginationObserver()

    await observer.on_download("https://example.com", "foo.txt", b"foo")
    observer.on_paginate("https://example.com/page2")

    with pytest.raises(StopAsyncIteration):
        await observer.on_download("https://example.com", "foo.txt", b"foo")


@pytest.mark.asyncio
async def test_stop_pagination_observer_no_duplicate_data():
    observer = StopPaginationObserver()
    await observer.on_save_data({"foo": "bar"})
    observer.on_paginate("https://example.com/page2")
    await observer.on_save_data({"baz": "qux"})
    await observer.on_save_data({"foo": [
        "bar",
        "baz",
    ]})


@pytest.mark.asyncio
async def test_ignore_underscore_attributes():
    observer = StopPaginationObserver()

    await observer.on_save_data({"foo": "bar", "__url": "qux"})

    observer.on_paginate("https://example.com/page2")
    await observer.on_save_data({"qux": "bar", "__url": "qux"})

    with pytest.raises(StopAsyncIteration):
        await observer.on_save_data({"foo": "bar", "__url": "bad boy asim"})


@pytest.mark.asyncio
async def test_duplicate_data_without_pagination():
    observer = StopPaginationObserver()
    await observer.on_save_data({"foo": "bar"})
    await observer.on_save_data({"foo": "bar"})

    await observer.on_queue_url("https://example.com", {"foo": "bar"})
    await observer.on_queue_url("https://example.com", {"foo": "bar"})

    await observer.on_download("https://example.com", "foo.txt", b"foo")
    await observer.on_download("https://example.com", "foo.txt", b"foo")

    observer.on_paginate("https://example.com/page2")
    with pytest.raises(StopAsyncIteration):
        await observer.on_save_data({"foo": "bar"})

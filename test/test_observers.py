import pytest

from harambe.observer import DuplicateHandler, InMemoryObserver


@pytest.mark.asyncio
async def in_memory_on_save_data():
    observer = InMemoryObserver()

    await observer.on_save_data({"foo": "bar"})
    await observer.on_save_data({"baz": "qux"})

    assert observer.data == [{"foo": "bar"}, {"baz": "qux"}]


@pytest.mark.asyncio
async def in_memory_on_queue_url():
    observer = InMemoryObserver()

    await observer.on_queue_url("https://example.com", {"foo": "bar"}, {"test": "test"})
    await observer.on_queue_url("https://example.org", {"baz": "qux"}, {"other": "other"})

    assert observer.urls == [
        ("https://example.com", {"foo": "bar"}, {"test": "test"}),
        ("https://example.org", {"baz": "qux"}, {"other": "other"}),
    ]


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_data_error():
    observer = DuplicateHandler()

    unduplicated = await observer.on_save_data({"foo": "bar"})
    await observer.on_paginate("https://example.com/page2")
    duplicated = await observer.on_save_data({"foo": "bar"})

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        await observer.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_url_error():
    observer = DuplicateHandler()

    unduplicated = await observer.on_queue_url("https://example.com", {"foo": "bar"}, {})
    await observer.on_paginate("https://example.com/page2")
    duplicated = await observer.on_queue_url("https://example.com", {"foo": "bar"}, {})

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        await observer.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_download_error():
    observer = DuplicateHandler()

    unduplicated = await observer.on_download("https://example.com", "foo.txt", b"foo")
    await observer.on_paginate("https://example.com/page2")
    duplicated = await observer.on_download("https://example.com", "foo.txt", b"foo")

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        await observer.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_no_duplicate_data():
    observer = DuplicateHandler()
    unduplicated1 = await observer.on_save_data({"foo": "bar"})
    await observer.on_paginate("https://example.com/page2")
    unduplicated2 = await observer.on_save_data({"baz": "qux"})
    unduplicated3 = await observer.on_save_data(
        {
            "foo": [
                "bar",
                "baz",
            ]
        }
    )

    assert not unduplicated1 and not unduplicated2 and not unduplicated3


@pytest.mark.asyncio
async def test_ignore_underscore_attributes():
    observer = DuplicateHandler()

    unduplicated1 = await observer.on_save_data({"foo": "bar", "__url": "qux"})
    unduplicated2 = await observer.on_save_data({"qux": "bar", "__url": "qux"})
    await observer.on_paginate("https://example.com/page2")

    duplicated1 = await observer.on_save_data({"foo": "bar", "__url": "bad boy asim"})
    duplicated2 = await observer.on_save_data({"qux": "bar", "__url": "bad boy adam"})

    assert not unduplicated1 and not unduplicated2 and duplicated1 and duplicated2

    with pytest.raises(StopAsyncIteration):
        await observer.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_duplicate_data_without_pagination():
    observer = DuplicateHandler()
    un_duplicated = await observer.on_save_data({"foo": "bar"})
    duplicated = await observer.on_save_data({"foo": "bar"})
    assert not un_duplicated and duplicated

    un_duplicated = await observer.on_queue_url("https://example.com", {"foo": "bar"}, {})
    duplicated = await observer.on_queue_url("https://example.com", {"foo": "bar"}, {})
    assert not un_duplicated and duplicated

    un_duplicated = await observer.on_download("https://example.com", "foo.txt", b"foo")
    duplicated = await observer.on_download("https://example.com", "foo.txt", b"foo")
    assert not un_duplicated and duplicated

    await observer.on_paginate("https://example.com/page2")

    duplicated = await observer.on_save_data({"foo": "bar"})
    assert duplicated

    with pytest.raises(StopAsyncIteration):
        await observer.on_paginate("https://example.com/page3")

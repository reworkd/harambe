import pytest

from harambe.observer import InMemoryObserver


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
    await observer.on_queue_url(
        "https://example.org", {"baz": "qux"}, {"other": "other"}
    )

    assert observer.urls == [
        ("https://example.com", {"foo": "bar"}, {"test": "test"}),
        ("https://example.org", {"baz": "qux"}, {"other": "other"}),
    ]

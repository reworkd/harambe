import pytest
import asyncio
from urllib.parse import quote

from harambe_core.observer.serialization_observer import SerializationObserver


@pytest.fixture
def published_events():
    return []


@pytest.fixture
def observer(published_events):
    def serializer(payload):
        return payload

    def sink(payload):
        published_events.append(payload)

    return SerializationObserver(sink, serializer)


def test_on_save_data(observer, published_events):
    asyncio.run(observer.on_save_data({"foo": "bar"}))
    assert len(published_events) == 1
    assert published_events[0] == {
        "type": "on_save_data",
        "data": {"foo": "bar"},
    }


def test_on_queue_url(observer, published_events):
    asyncio.run(
        observer.on_queue_url(
            "http://example.com", {"some": "context"}, {"optionA": True}
        )
    )
    assert len(published_events) == 1
    assert published_events[0] == {
        "type": "on_queue_url",
        "data": {
            "url": "http://example.com",
            "context": {"some": "context"},
            "options": {"optionA": True},
        },
    }


def test_on_download(observer, published_events):
    content = b"Hello World!"
    download_meta = asyncio.run(
        observer.on_download("http://files.example.com", "test.txt", content, "path")
    )
    assert len(published_events) == 1
    assert published_events[0] == {
        "type": "on_download",
        "data": {
            "download_url": "http://files.example.com",
            "filename": "test.txt",
            "content": "SGVsbG8gV29ybGQh",
            "path": "path",
        },
    }
    assert download_meta["url"] == f"http://files.example.com/{quote('test.txt')}"
    assert download_meta["filename"] == "test.txt"


def test_on_paginate(observer, published_events):
    asyncio.run(observer.on_paginate("http://example.com/next"))
    assert len(published_events) == 0


def test_on_save_cookies(observer, published_events):
    cookies = [{"name": "session", "value": "abc123"}]
    asyncio.run(observer.on_save_cookies(cookies))
    assert len(published_events) == 1
    assert published_events[0] == {
        "type": "on_save_cookies",
        "data": cookies,
    }


def test_on_save_local_storage(observer, published_events):
    items = [{"key": "theme", "value": "dark"}]
    asyncio.run(observer.on_save_local_storage(items))
    assert len(published_events) == 1
    assert published_events[0] == {
        "type": "on_save_local_storage",
        "data": items,
    }


def test_multiple_events(observer, published_events):
    asyncio.run(observer.on_save_data({"foo": "bar"}))
    asyncio.run(
        observer.on_queue_url(
            "http://example.com", {"some": "context"}, {"optionA": True}
        )
    )
    assert len(published_events) == 2
    assert published_events[0] == {
        "type": "on_save_data",
        "data": {"foo": "bar"},
    }
    assert published_events[1] == {
        "type": "on_queue_url",
        "data": {
            "url": "http://example.com",
            "context": {"some": "context"},
            "options": {"optionA": True},
        },
    }

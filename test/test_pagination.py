import pytest

from harambe.pagination import PaginatedList, DuplicateHandler


@pytest.fixture
def paginated_collection():
    return PaginatedList()


@pytest.fixture
def duplicate_handler():
    return DuplicateHandler()


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_data_error(duplicate_handler):
    unduplicated = duplicate_handler.on_save_data({"foo": "bar"})
    duplicate_handler.on_paginate("https://example.com/page2")
    duplicated = duplicate_handler.on_save_data({"foo": "bar"})

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        duplicate_handler.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_url_error(duplicate_handler):
    unduplicated = duplicate_handler.on_queue_url(
        "https://example.com", {"foo": "bar"}, {}
    )
    duplicate_handler.on_paginate("https://example.com/page2")
    duplicated = duplicate_handler.on_queue_url(
        "https://example.com", {"foo": "bar"}, {}
    )

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        duplicate_handler.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_duplicate_download_error(duplicate_handler):
    unduplicated = duplicate_handler.on_download(
        "https://example.com", "foo.txt", b"foo"
    )
    duplicate_handler.on_paginate("https://example.com/page2")
    duplicated = duplicate_handler.on_download("https://example.com", "foo.txt", b"foo")

    assert not unduplicated and duplicated

    with pytest.raises(StopAsyncIteration):
        duplicate_handler.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_stop_pagination_observer_no_duplicate_data(duplicate_handler):
    unduplicated1 = duplicate_handler.on_save_data({"foo": "bar"})
    duplicate_handler.on_paginate("https://example.com/page2")
    unduplicated2 = duplicate_handler.on_save_data({"baz": "qux"})
    unduplicated3 = duplicate_handler.on_save_data(
        {
            "foo": [
                "bar",
                "baz",
            ]
        }
    )

    assert not unduplicated1 and not unduplicated2 and not unduplicated3


@pytest.mark.asyncio
async def test_ignore_underscore_attributes(duplicate_handler):
    unduplicated1 = duplicate_handler.on_save_data({"foo": "bar", "__url": "qux"})
    unduplicated2 = duplicate_handler.on_save_data({"qux": "bar", "__url": "qux"})
    duplicate_handler.on_paginate("https://example.com/page2")

    duplicated1 = duplicate_handler.on_save_data(
        {"foo": "bar", "__url": "bad boy asim"}
    )
    duplicated2 = duplicate_handler.on_save_data(
        {"qux": "bar", "__url": "bad boy adam"}
    )

    assert not unduplicated1 and not unduplicated2 and duplicated1 and duplicated2

    with pytest.raises(StopAsyncIteration):
        duplicate_handler.on_paginate("https://example.com/page3")


@pytest.mark.asyncio
async def test_duplicate_data_without_pagination(duplicate_handler):
    un_duplicated = duplicate_handler.on_save_data({"foo": "bar"})
    duplicated = duplicate_handler.on_save_data({"foo": "bar"})
    assert not un_duplicated and duplicated

    un_duplicated = duplicate_handler.on_queue_url(
        "https://example.com", {"foo": "bar"}, {}
    )
    duplicated = duplicate_handler.on_queue_url(
        "https://example.com", {"foo": "bar"}, {}
    )
    assert not un_duplicated and duplicated

    un_duplicated = duplicate_handler.on_download(
        "https://example.com", "foo.txt", b"foo"
    )
    duplicated = duplicate_handler.on_download("https://example.com", "foo.txt", b"foo")
    assert not un_duplicated and duplicated

    duplicate_handler.on_paginate("https://example.com/page2")

    duplicated = duplicate_handler.on_save_data({"foo": "bar"})
    assert duplicated

    with pytest.raises(StopAsyncIteration):
        duplicate_handler.on_paginate("https://example.com/page3")


def test_append(paginated_collection):
    assert not len(paginated_collection)
    assert paginated_collection.should_continue()

    paginated_collection.append(1)
    assert len(paginated_collection) == 1
    assert paginated_collection.should_continue()

    paginated_collection.append(2)
    assert len(paginated_collection) == 2
    assert paginated_collection.should_continue()

    paginated_collection.append(1)
    assert len(paginated_collection) == 2
    assert not paginated_collection.should_continue()


def test_extend(paginated_collection):
    paginated_collection.extend(
        [{"foo": "bar"}, {"baz": "qux"}, {"foo": "bar", "baz": "qux"}]
    )
    assert len(paginated_collection) == 3
    assert paginated_collection.should_continue()

    paginated_collection.extend([{"adam": "eve"}, {"adam": {"eve": "adam"}}])
    assert len(paginated_collection) == 5
    assert paginated_collection.should_continue()

    paginated_collection.extend([{"foo": "bar", "baz": "qux"}, {"eve": "adam"}])
    assert len(paginated_collection) == 6
    assert not paginated_collection.should_continue()

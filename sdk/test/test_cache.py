from harambe.cache import single_value_cache


async def test_single_value_cache(mocker):
    mock_fn = mocker.AsyncMock(return_value="result")

    class Dummy:
        def __init__(self):
            self._cache = None

        @single_value_cache("_cache")
        async def f(self, key):
            return await mock_fn(key)

    c = Dummy()

    # first call: cache miss
    r1 = await c.f("a")
    assert r1 == "result"
    assert mock_fn.await_count == 1

    # second call same key: cache hit
    r2 = await c.f("a")
    assert r2 == "result"
    assert mock_fn.await_count == 1

    # new key: cache miss
    r3 = await c.f("b")
    assert r3 == "result"
    assert mock_fn.await_count == 2

    # again "b": hit
    r4 = await c.f("b")
    assert r4 == "result"
    assert mock_fn.await_count == 2

    # new key: cache miss
    r5 = await c.f("a")
    assert r5 == "result"

    assert mock_fn.await_count == 3

    # new key: cache miss
    r6 = await c.f("c")
    assert r6 == "result"

    assert mock_fn.await_count == 4

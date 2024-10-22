import asyncio

from harambe.user_agent import compute_user_agent, random_user_agent


async def test_user_agent_with_string():
    result = await compute_user_agent("my-user-agent")
    assert result == "my-user-agent"


async def test_user_agent_with_sync_callable():
    def sync_callable() -> str:
        return "sync-user-agent"

    result = await compute_user_agent(sync_callable)
    assert result == "sync-user-agent"

    res = await compute_user_agent(random_user_agent)
    assert res
    assert isinstance(res, str)


async def test_user_agent_with_async_callable():
    async def async_callable() -> str:
        await asyncio.sleep(0.1)
        return "async-user-agent"

    result = await compute_user_agent(async_callable)
    assert result == "async-user-agent"


def test_default_user_agent():
    res = random_user_agent()
    assert res
    assert isinstance(res, str)

import asyncio
from typing import Callable, Awaitable

import ua_generator

UserAgentFactory = str | Callable[[], str | Awaitable[str]]


def random_user_agent() -> str:
    ua = ua_generator.generate(device="desktop", browser=("chrome", "edge"))
    return ua.headers.get()["user-agent"]


async def compute_user_agent(factory: UserAgentFactory) -> str:
    if not callable(factory):
        return factory

    result = factory()
    if asyncio.iscoroutine(result):
        return await result

    return result

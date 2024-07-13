from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Callable, Awaitable

from curl_cffi.requests import AsyncSession

from harambe.contrib.soup.impl import SoupPage


PageFactory = Callable[..., Awaitable[SoupPage]]


@asynccontextmanager
async def soup_harness(
    proxy: str | None = None, **__: Any
) -> AsyncGenerator[PageFactory, None]:
    async with AsyncSession(proxy=proxy, impersonate="chrome", verify=False) as s:

        async def factory() -> SoupPage:
            return SoupPage(s)

        yield factory

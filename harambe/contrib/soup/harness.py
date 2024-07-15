from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Callable, Awaitable, Sequence

from curl_cffi.requests import AsyncSession

from harambe.contrib.soup.impl import SoupPage
from harambe.types import SetCookieParam

PageFactory = Callable[..., Awaitable[SoupPage]]


@asynccontextmanager
async def soup_harness(
    *, proxy: str | None = None, cookies: Sequence[SetCookieParam] = (), **__: Any
) -> AsyncGenerator[PageFactory, None]:
    async with AsyncSession(proxy=proxy, impersonate="chrome", verify=False) as s:
        for c in cookies:
            s.cookies.set(
                name=c["name"],
                value=c["value"],
                domain=c.get("domain", ""),
                path=c.get("path", "/"),
                secure=c.get("secure", False),
            )

        async def factory(*_: Any, **__: Any) -> SoupPage:
            return SoupPage(s)

        yield factory

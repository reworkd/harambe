from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Callable, Awaitable, Sequence, Optional

from curl_cffi.requests import AsyncSession

from harambe.contrib.soup.impl import SoupPage
from harambe.contrib.soup.tracing import Tracer
from harambe.types import SetCookieParam

Callback = Callable[[Tracer], Awaitable[None]]
PageFactory = Callable[..., Awaitable[SoupPage]]


@asynccontextmanager
async def soup_harness(
    *,
    proxy: str | None = None,
    cookies: Sequence[SetCookieParam] = (),
    on_start: Optional[Callback] = None,
    on_end: Optional[Callback] = None,
    **__: Any,
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

        tracer = Tracer()

        async def factory(*_: Any, **__: Any) -> SoupPage:
            return SoupPage(s, tracer=tracer)

        try:
            if on_start:
                await on_start(tracer)

            yield factory
        finally:
            if on_end:
                await on_end(tracer)

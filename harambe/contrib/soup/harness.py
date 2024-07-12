from contextlib import asynccontextmanager
from typing import AsyncGenerator

from curl_cffi.requests import AsyncSession

from harambe.contrib.soup.impl import SoupPage


@asynccontextmanager
async def soup_harness(
    headless: bool,
    cdp_endpoint: str | None,
    proxy: str | None = None,
) -> AsyncGenerator[SoupPage, None]:
    if cdp_endpoint:
        raise ValueError("CDP endpoint is not supported for Soup")

    async with AsyncSession(proxy=proxy, impersonate="chrome") as s:
        yield SoupPage(s)

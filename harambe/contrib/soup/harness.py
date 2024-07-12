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
    """
    Context manager for Playwright. Starts a new browser, context, and page, and closes them when done.
    Also does some basic setup like setting the viewport, user agent, ignoring HTTPS errors, creation of HAR file, and stealth.

    :param headless: launch browser in headless mode
    :param cdp_endpoint: Chrome DevTools Protocol endpoint to connect to (if using a remote browser)
    :param proxy: proxy server to use
    :return: async generator yielding a Playwright page
    """
    if cdp_endpoint:
        raise ValueError("CDP endpoint is not supported for Soup")

    async with AsyncSession(proxy=proxy) as s:
        yield SoupPage(s)

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable, Optional, Sequence, cast

import ua_generator
from playwright.async_api import BrowserContext, ViewportSize, async_playwright, Page
from playwright_stealth import stealth_async

from harambe.contrib.playwright.impl import PlaywrightPage
from harambe.handlers import UnnecessaryResourceHandler
from harambe.proxy import proxy_from_url
from harambe.types import SetCookieParam, BrowserType

Callback = Callable[[BrowserContext], Awaitable[None]]
PageCallback = Callable[[Page], Awaitable[None]]
PageFactory = Callable[..., Awaitable[PlaywrightPage]]

DEFAULT_VIEWPORT: ViewportSize = {"width": 1440, "height": 1024}


@asynccontextmanager
async def playwright_harness(
    *,
    headless: bool = True,
    cdp_endpoint: str | None = None,
    proxy: str | None = None,
    cookies: Sequence[SetCookieParam] = (),
    headers: dict[str, str] | None = None,
    stealth: bool = False,
    default_timeout: int = 30000,
    abort_unnecessary_requests: bool = True,
    user_agent: Optional[str] = None,
    viewport: Optional[ViewportSize] = None,
    on_start: Optional[Callback] = None,
    on_end: Optional[Callback] = None,
    on_new_page: Optional[PageCallback] = None,
    browser_type: Optional[BrowserType] = None,
    enable_clipboard: bool = False,
    **__: Any,
) -> AsyncGenerator[PageFactory, None]:
    """
    Context manager for Playwright. Starts a new browser, context, and page, and closes them when done.
    Also does some basic setup like setting the viewport, user agent, ignoring HTTPS errors,
    creation of HAR file, and stealth.
    """
    async with async_playwright() as p:
        browser = await (
            p.chromium.connect_over_cdp(endpoint_url=cdp_endpoint)
            if cdp_endpoint
            else getattr(p, cast(str, browser_type or "chromium")).launch(
                headless=headless,
                args=[
                    *(
                        # Disables navigator.webdriver showing up
                        ["--disable-blink-features=AutomationControlled"]
                        if browser_type == "chromium"
                        else []
                    ),
                    *(
                        # New chromium headless mode
                        ["--headless=new"] if headless else []
                    ),
                ],
            )
        )

        # TODO: More intelligently generate based on current system specs
        # randomly generating agents will create inconsistent fingerprints
        ua = ua_generator.generate(device="desktop", browser=("chrome", "edge"))
        user_agent = user_agent if user_agent else ua.headers.get()["user-agent"]

        ctx = await browser.new_context(
            viewport=viewport or DEFAULT_VIEWPORT,
            ignore_https_errors=True,
            user_agent=user_agent,
            proxy=proxy_from_url(proxy) if proxy else None,
            permissions=["clipboard-read", "clipboard-write"]
            if enable_clipboard
            else None,
        )

        ctx.set_default_timeout(default_timeout)

        if cookies:
            await ctx.add_cookies(cookies)

        if abort_unnecessary_requests:
            await ctx.route("**/*", UnnecessaryResourceHandler().handle)

        async def page_factory(*_: Any, **__: Any) -> PlaywrightPage:
            page = await ctx.new_page()
            if on_new_page:
                await on_new_page(page)
            if stealth:
                await stealth_async(page)
            if headers:
                await page.set_extra_http_headers(headers)
            return page  # type: ignore

        try:
            if on_start:
                await on_start(ctx)
            yield page_factory
        finally:
            try:
                if on_end:
                    await on_end(ctx)
            finally:
                await ctx.close()
                await browser.close()

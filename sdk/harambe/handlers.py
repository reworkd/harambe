import re
from abc import ABC
from typing import Any, Literal, Self

from playwright.async_api import Page, Route

ResourceType = Literal[
    "document",
    "stylesheet",
    "image",
    "media",
    "font",
    "script",
    "texttrack",
    "xhr",
    "fetch",
    "eventsource",
    "websocket",
    "manifest",
    "other",
    "*",
]


class AbstractHandler(ABC):
    async def handle(self, route: Route) -> None:
        raise NotImplementedError


class ResourceRequestHandler(AbstractHandler):
    def __init__(
        self,
        page: Page,
        resource_type: ResourceType,
        url_pattern: str = "**/*",
    ):
        self.page = page
        self.url_pattern = url_pattern
        self.resource_type = resource_type

        self._initial_pages = [p.url for p in page.context.pages]
        self._new_pages: list[str] = []

    async def __aenter__(self) -> Self:
        await self.page.context.route(self.url_pattern, self.handle)
        return self

    async def __aexit__(self, *_: Any, **__: Any) -> None:
        await self.page.context.unroute(self.url_pattern, self.handle)
        await self.page.bring_to_front()
        for page in self.page.context.pages:
            if page.url not in self._initial_pages:
                self._new_pages.append(page.url)
                await page.close()

    async def handle(self, route: Route) -> None:
        if (
            self.resource_type == "*"
            or self.resource_type in route.request.resource_type
        ):
            await route.fulfill(
                status=200,
                content_type="text/plain",
                body="Intercepted by the handler",
            )
            return

        await route.fallback()

    def captured_url(self) -> str | None:
        if len(self._new_pages) > 1:
            raise ValueError("More than one page matched")

        return self._new_pages[0] if self._new_pages else None


class UnnecessaryResourceHandler(AbstractHandler):
    async def handle(self, route: Route) -> None:
        resource_type = route.request.resource_type
        url = route.request.url

        if (
            resource_type in ["image", "media", "font"]
            or re.match(r"^data:(image|audio|video)", url)
            or re.match(r"social-widget|tracking-script|ads", url)
        ):
            await route.abort("blockedbyclient")
            return

        await route.fallback()

import re
from abc import ABC
from typing import Literal

from playwright.async_api import Route, Page

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
]


class AbstractHandler(ABC):
    async def handle(self, route: Route) -> None:
        raise NotImplementedError


class ResourceRequestHandler(AbstractHandler):
    def __init__(
        self,
        page: Page,
        resource_type: ResourceType,
        abort_on_match: bool,
        url_pattern: str = "**/*",
    ):
        self.page = page
        self.resource_type = resource_type
        self.abort_on_match = abort_on_match
        self.url_pattern = url_pattern
        self.matched_requests = []

    async def __aenter__(self):
        await self.page.context.route(self.url_pattern, self.handle)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.page.context.unroute(self.url_pattern, self.handle)
        await self.page.bring_to_front()

    async def handle(self, route: Route) -> None:
        if self.resource_type in route.request.resource_type:
            self.matched_requests.append(route.request)
            if self.abort_on_match:
                await route.abort("blockedbyclient")
                return

        await route.fallback()

    @property
    def matched_url(self) -> str | None:
        if len(self.matched_requests) > 1:
            raise ValueError("More than one request matched")

        return self.matched_requests[0].url if self.matched_requests else None


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

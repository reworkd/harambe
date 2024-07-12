from playwright.async_api import ElementHandle, Page

from harambe.contrib.types import AbstractElementHandle, AbstractPage


class PlaywrightElementHandle(ElementHandle, AbstractElementHandle):
    pass


class PlaywrightPage(Page, AbstractPage[PlaywrightElementHandle]):
    pass

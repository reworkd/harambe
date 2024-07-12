from pathlib import Path

import pytest
from aiohttp import web

from harambe import SDK
from harambe.observer import InMemoryObserver


@pytest.fixture(scope="module")
def mock_html_folder():
    path = Path(__file__).parent / "mock_html"
    assert path.exists() and path.is_dir() and len(list(path.iterdir())) > 0
    return path


@pytest.fixture
async def server(mock_html_folder):
    async def handle(request):
        return web.FileResponse(mock_html_folder / "simple_page_with_table.html")

    app = web.Application()
    app.router.add_get(path="", handler=handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8081)
    await site.start()

    yield "http://127.0.0.1:8081/"

    await runner.cleanup()


@pytest.fixture
async def observer():
    return InMemoryObserver()


async def test_save_data(server, observer):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page

        for row in await page.query_selector_all("tbody > tr"):
            fruit, price = await row.query_selector_all("td")
            await sdk.save_data(
                {"fruit": await fruit.inner_text(), "price": await price.inner_text()}
            )

    await SDK.run(scraper=scraper, url=server, schema={}, headless=True)

    assert len(observer.data) == 3

    assert observer.data[0]["fruit"] == "Apple"
    assert observer.data[0]["price"] == "1.00"
    assert observer.data[0]["__url"] == server

    assert not observer.urls
    assert not observer.files


async def test_enqueue_data(server, observer):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        await sdk.enqueue("?page=1")
        await sdk.enqueue("/terms", "https://reworkd.ai")

    await SDK.run(scraper=scraper, url=server, schema={}, headless=True)

    assert not observer.data
    assert len(observer.urls) == 3
    assert observer.urls[0][0] == f"{server}?page=1"
    assert observer.urls[1][0] == f"{server}terms"
    assert observer.urls[2][0] == "https://reworkd.ai"

    assert observer.urls[0][1] == {"__url": server}
    assert observer.urls[1][1] == {"__url": server}
    assert observer.urls[2][1] == {"__url": server}


async def test_enqueue_data_with_context(server, observer):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        await sdk.enqueue("/adam/?page=55", context={"last": "Watkins"})

    await SDK.run(scraper=scraper, url=server, schema={}, headless=True)

    assert not observer.data
    assert len(observer.urls) == 1
    assert observer.urls[0][0] == f"{server}adam/?page=55"
    assert observer.urls[0][1] == {"__url": server, "last": "Watkins"}


async def test_enqueue_coro(server, observer):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await sdk.enqueue((await page.query_selector("a")).get_attribute("href"))

    await SDK.run(scraper=scraper, url=server, schema={}, headless=True)
    assert len(observer.urls) == 1
    assert observer.urls[0][0] == f"{server}other"

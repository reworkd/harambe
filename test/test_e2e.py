from pathlib import Path
from typing import cast

import pytest
from aiohttp import web

from harambe import SDK
from harambe.contrib import playwright_harness, soup_harness
from harambe.observer import InMemoryObserver
from harambe.parser.parser import SchemaValidationError
from harambe.parser.schemas import Schemas
from harambe.types import BrowserType


@pytest.fixture(scope="module")
def mock_html_folder():
    path = Path(__file__).parent / "mock_html"
    assert path.exists() and path.is_dir() and len(list(path.iterdir())) > 0
    return path


@pytest.fixture
async def server(mock_html_folder):
    async def handle(request):
        file_path = mock_html_folder / f"{request.path.strip('/')}.html"
        if not file_path.exists():
            return web.FileResponse(mock_html_folder / "404.html")

        return web.FileResponse(file_path)

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8081)
    await site.start()

    yield site.name.strip("/")

    await runner.cleanup()


@pytest.fixture
def observer():
    return InMemoryObserver()


@pytest.mark.parametrize("browser_type", ["chromium", "firefox", "webkit"])
@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_save_data(server, observer, harness, browser_type):
    url = f"{server}/table"

    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page

        await page.wait_for_load_state()
        for row in await page.query_selector_all("tbody > tr"):
            fruit, price = await row.query_selector_all("td")

            await sdk.save_data(
                {"fruit": await fruit.inner_text(), "price": await price.inner_text()}
            )

    browser_type = cast(BrowserType, browser_type)
    await SDK.run(
        scraper=scraper,
        url=url,
        schema={},
        headless=True,
        harness=harness,
        browser_type=browser_type,
    )

    assert len(observer.data) == 3

    assert observer.data[0]["fruit"] == "Apple"
    assert observer.data[0]["price"] == "1.00"
    assert observer.data[0]["__url"] == url

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
    assert observer.urls[0][0] == f"{server}/?page=1"
    assert observer.urls[1][0] == f"{server}/terms"
    assert observer.urls[2][0] == "https://reworkd.ai"

    url = f"{server}/"
    assert observer.urls[0][1] == {"__url": url}
    assert observer.urls[1][1] == {"__url": url}
    assert observer.urls[2][1] == {"__url": url}


async def test_enqueue_data_with_context(server, observer):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        await sdk.enqueue("/adam/?page=55", context={"last": "Watkins"})

    await SDK.run(scraper=scraper, url=server, schema={}, headless=True)

    assert not observer.data
    assert len(observer.urls) == 1
    assert observer.urls[0][0] == f"{server}/adam/?page=55"
    assert observer.urls[0][1] == {"__url": f"{server}/", "last": "Watkins"}


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_enqueue_coro(server, observer, harness):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await sdk.enqueue((await page.query_selector("a")).get_attribute("href"))

    await SDK.run(
        scraper=scraper,
        url=f"{server}/table",
        schema={},
        headless=True,
        harness=harness,
    )
    assert len(observer.urls) == 1
    assert observer.urls[0][0] == f"{server}/other"


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_paginate(server, observer, harness):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await sdk.save_data({"content": await page.content()})

        async def pager():
            link = await page.query_selector("a")
            return await link.get_attribute("href")

        await sdk.paginate(pager)

    await SDK.run(
        scraper=scraper,
        url=f"{server}/table",
        schema={},
        headless=True,
        harness=harness,
    )

    assert len(observer.data) == 2
    assert observer.data[0]["content"]
    assert observer.data[0]["__url"] == f"{server}/table"

    assert observer.data[1]["content"]
    assert observer.data[1]["__url"] == f"{server}/other"


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_narcotics(server, observer, harness):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs) -> None:
        page = sdk.page
        await page.wait_for_selector("div#ds-content")

        document_url_elements = await page.query_selector_all("div.file-wrapper")

        data = []
        for doc in document_url_elements:
            title_element = await doc.query_selector("div.file-metadata span[title]")
            title = (await title_element.get_attribute("title")).replace(".pdf", "")

            document_url_element = await doc.query_selector("a.image-link")
            document_url = await document_url_element.get_attribute("href")

            data.append({"title": title, "document_url": document_url})

        for item in data:
            await sdk.save_data(item)

    await SDK.run(
        scraper=scraper,
        url=f"{server}/narcotics",
        schema={},
        headless=True,
        harness=harness,
    )

    assert len(observer.data) == 1
    assert observer.data[0] == {
        "title": "NARCOTICS CONTROL COMMISSION ACT, 2020 (ACT 1019)",
        "document_url": "/bitstream/handle/123456789/1921/meth.pdf?sequence=1&isAllowed=y",
        "__url": f"{server}/narcotics",
    }


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_regulations(server, observer, harness):
    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs) -> None:
        page = sdk.page
        await page.wait_for_selector("table.table.mb-0.table-hover.table-striped")

        links = await page.query_selector_all(
            "a[title='Go to the Regulations page'] + ul a"
        )
        for link in links:
            href = await link.get_attribute("href")
            await sdk.enqueue(href)

    await SDK.run(
        scraper=scraper,
        url=f"{server}/regulations",
        schema={},
        headless=True,
        harness=harness,
    )

    assert not observer.data
    assert len(observer.urls) == 3
    assert observer.urls[0][0] == f"{server}/regulations/act/"
    assert observer.urls[1][0] == f"{server}/regulations/regulations/"
    assert observer.urls[2][0] == f"{server}/regulations/guidelines/"
    assert observer.urls[0][1] == {"__url": f"{server}/regulations"}
    assert observer.urls[1][1] == {"__url": f"{server}/regulations"}
    assert observer.urls[2][1] == {"__url": f"{server}/regulations"}


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_text_content(server, observer, harness):
    url = f"{server}/table"

    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        content = await page.text_content("table")
        await sdk.save_data({"page_content": content})

        table = await page.query_selector("table")
        await sdk.save_data({"table_content": await table.text_content()})

    await SDK.run(scraper=scraper, url=url, schema={}, headless=True, harness=harness)
    assert len(observer.data) == 2

    assert observer.data[0]["page_content"] == observer.data[1]["table_content"]
    for text in ["Apple", "Orange", "Banana"]:
        assert (
            text in observer.data[0]["page_content"]
        ), f"{text} not in {observer.data[0]['page_content']}"
        assert (
            text in observer.data[1]["table_content"]
        ), f"{text} not in {observer.data[1]['table_content']}"


@pytest.mark.parametrize("harness", [soup_harness])
async def test_text_content_when_selector_does_not_exist(server, observer, harness):
    url = f"{server}/table"

    @SDK.scraper("test", "detail", observer=observer)
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await page.set_default_timeout(1)

        content = await page.text_content("table.non-existent")
        await sdk.save_data({"page_content": content})

    await SDK.run(scraper=scraper, url=url, schema={}, headless=True, harness=harness)
    assert len(observer.data) == 1
    assert observer.data[0]["page_content"] is None


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_page_goto_with_options(server, harness):
    url = f"{server}/table"

    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await page.goto(
            "https://example.com", timeout=1000, referer="https://google.com"
        )

    await SDK.run(scraper=scraper, url=url, schema={}, headless=True, harness=harness)


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_currency_validator(server, harness):
    async def scraper(sdk: SDK, *args, **kwargs):
        await sdk.save_data({"price": "$1,9999.00"})

    await SDK.run(
        scraper=scraper,
        url=f"{server}/table",
        schema={"price": {"type": "currency"}},
        headless=True,
        harness=harness,
    )


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_schema_validation_error_on_null_fields(server, harness):
    async def scraper(sdk: SDK, *args, **kwargs):
        invalid_data = {
            "title": None,
            "description": "",
            "classification": None,
            "is_cancelled": None,
            "start_time": None,
            "end_time": None,
            "is_all_day_event": "",
            "time_notes": "",
            "location": {},
            "links": [
                {
                    "title": "",
                    "url": None,
                }
            ],
        }
        await sdk.save_data(invalid_data)

    with pytest.raises(SchemaValidationError):
        await SDK.run(
            scraper=scraper,
            url=f"{server}/table",
            schema=Schemas.government_meetings,
            headless=True,
            harness=harness,
        )


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_strip_all_values(server, harness):
    async def scraper(sdk: SDK, *args, **kwargs):
        test_strip_values_data = {
            "  title  ": "test title   ",
            " description": "  test description   ",
            "classification ": " test classification",
            "is_cancelled  ": True,
            "start_time  ": "  05/29/2024 02:00:00 PM  ",
            "end_time": "December 17, 1995 03:24:00    ",
            " is_all_day_event": False,
            " time_notes": "     test trim       notes   ",
            "  location": {
                " name ": "test location name  ",
                "address   ": "    test address    ",
            },
            "links ": [
                {
                    "   title   ": "  ",
                    "   url": "  /example.com  ",
                },
            ],
        }
        await sdk.save_data(test_strip_values_data)

    await SDK.run(
        scraper=scraper,
        url=f"{server}/table",
        schema=Schemas.government_meetings,
        headless=True,
        harness=harness,
    )


@pytest.mark.parametrize("harness", [playwright_harness, soup_harness])
async def test_required_feilds(server, harness):
    async def scraper(sdk: SDK, *args, **kwargs):
        test_required_fields_schema = {
            "id": None,
            "title": "test title",
            "description": "test description",
            "location": "test location",
            "type": "test type",
            "category": "test category",
            "posted_date": "test posted date",
            "due_date": "test due date",
            "agency": "test agency",
            "contact_name": "test contact name",
            "contact_email": "test contact email",
            "contact_number": "test contact number",
            "attachments": [
                {"title": "test attachment title", "url": "test attachment url"}
            ],
        }
        await sdk.save_data(test_required_fields_schema)

    with pytest.raises(SchemaValidationError):
        await SDK.run(
            scraper=scraper,
            url=f"{server}/table",
            schema=Schemas.government_contracts_small,
            headless=True,
            harness=harness,
        )


@pytest.mark.parametrize("harness", [soup_harness])
async def test_disable_go_to_url_bug(server, harness):
    async def scraper(sdk: SDK, *args, **kwargs):
        page = sdk.page
        await sdk.save_data({"url": page.url})

    await SDK.run(
        scraper=scraper,
        disable_go_to_url=True,
        url="https://www.bcp.gov.gh/acc/registry/docs/Ghana%20Export%20Promotion%20Authority%20Act,%201969%20(NLCD%20396).pdf",
        schema={"url": {"type": "url"}},
        headless=True,
        harness=harness,
    )

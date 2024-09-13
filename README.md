<p align="center">
  <img src="./.github/assets/banner.png" height="200" alt="Tarsier Monkey" />
</p>

<h3 align="center">🦍 Harambe Web extraction SDK 🦍</h2>

# Harambe

Harambe is the extraction SDK for Reworkd. It provides a simple interface
for interacting with the web. It provides a unified interface and runtime
for both manual and automatically created web extractors

---

- [Setup and Installation](#setup-and-installation)
- [Folder Structure](#folder-structure)
- [Example Scraper](#example-scraper)
  - [Detail Only Scraper](#detail-only-scraper)
  - [Listing Scraper](#listing-scraper)
  - [Using Cache](#using-cache)
- [Running a Scraper](#running-a-scraper)
- [Submitting a PR](#submitting-a-pr)

---

## Setup and Installation

To install Harambe, clone the repository and install the requirements.
All requirements are managed via [poetry](https://python-poetry.org/).

```shell
git clone https://github.com/reworkd/harambe.git
poetry install
```

## Example Scraper

Generally scrapers come in two types, **listing** and detail **scrapers**. Listing
scrapers are used to collect a list of items to scrape. Detail scrapers
are used to scrape the details of a single item.

If all the items that you want to scrape are available on a single page,
then you can use a detail scraper to scrape all the items. If the
items are spread across multiple pages, then you will need to use a
listing scraper to collect the items and then use a detail scraper to
scrape the details of each item.

ALL scrapers must be decorated with `SDK.scraper`. This decorator
registers the scraper with the SDK and provides the SDK with the
necessary information to run the scraper.

#### Detail Only Scraper

Shown below is an example detail scraper. The `context` parameter is
used to pass data from the listing scraper to the detail scraper.
In this example, the `context` parameter is used to pass the phone

```python
import asyncio
import math
import re
from typing import Any
from playwright.async_api import Page
from harambe import SDK, Schemas
from harambe import PlaywrightUtils as Pu

@SDK.scraper(
    domain="https://food.kp.gov.pk",
    stage="detail",
)
async def scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.goto(url)
    await page.wait_for_selector("#main_content a")
    cards = await page.query_selector_all("#main_content a")
    for card in cards:
        title = await card.inner_text()
        href = await card.get_attribute("href")
        if title and href:
            await sdk.save_data(
                {
                    "title": title,
                    "document_url": href,
                }
            )


if __name__ == "__main__":
    asyncio.run(
        SDK.run(
            scrape,
            "https://food.kp.gov.pk/page/rules_and_regulations",
            schema={},
        )
    )

```

#### Listing Scraper

Shown below is an example listing scraper. Use `SDK.enqueue` to to add
urls that will need be scraped by the detail scraper. The `context`
parameter is used to pass data from the listing scraper to the detail
scraper.

```python
import asyncio
import math
import re
from typing import Any
from playwright.async_api import Page
from harambe import SDK
from harambe import PlaywrightUtils as Pu

@SDK.scraper(
    domain="https://kpcode.kp.gov.pk",
    stage="listing",
)
async def listing_scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.wait_for_selector(".artlist a")
    docs = await page.query_selector_all(".artlist a")
    for doc in docs:
        href = await doc.get_attribute("href")
        await sdk.enqueue(href)

    async def pager():
        next_page_element = await page.query_selector("li[title='Next'] > a")
        return next_page_element

    await sdk.paginate(pager)


@SDK.scraper(
    domain="https://kpcode.kp.gov.pk",
    stage="detail",
)
async def detail_scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.wait_for_selector(".header_h2")
    title = await Pu.get_text(page, ".header_h2")
    link = await Pu.get_link(page, "a[href*=pdf]")
    await sdk.save_data({"title": title, "document_url ": link})


if __name__ == "__main__":
    asyncio.run(
        SDK.run(
            listing_scrape,
            "https://kpcode.kp.gov.pk/homepage/list_all_law_and_rule/879351",
            headless=False,
            schema={},
        )
    )
    asyncio.run(SDK.run_from_file(detail_scrape, schema={}))

```

#### Using Cache

The code below is an example detail scraper that relies on HAR cache
that it creates during initial run, subsequently using it as source
of data to improve speed and consume less bandwidth.

```python
import asyncio
import os.path
from typing import Any

from playwright.async_api import Page

from harambe import SDK
from harambe import PlaywrightUtils as Pu

HAR_FILE_PATH = "bananas.har"
SELECTORS = {
    "last_page": "",
    "list_view": "//div[@class='et_pb_blurb_content']",
    "name": "//h4/*[self::span or self::a]",
    "fax": ">Fax.*?strong>(.*?)<br>",
    # etc...
}


async def setup(sdk: SDK) -> None:
    page: Page = sdk.page

    already_cached = os.path.isfile(HAR_FILE_PATH)

    if already_cached:
        await page.route_from_har(HAR_FILE_PATH, not_found="fallback")
    else:
        await page.route_from_har(HAR_FILE_PATH, not_found="fallback", update=True)


# Annotation registers the scraper with the SDK
@SDK.scraper(domain="https://apprhs.org/our-locations/", stage="detail")
async def scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page

    locations = await page.locator(SELECTORS["list_view"]).all()
    for location in locations:
        # Save the data to the database or file
        await sdk.save_data(
            {
                "name": await Pu.get_text(location, SELECTORS["name"]),
                "fax": await Pu.parse_by_regex(location, SELECTORS["fax"]),
                # etc...
            }
        )


if __name__ == "__main__":
    asyncio.run(SDK.run(scrape, "https://apprhs.org/our-locations/", setup=setup , schema= {}))
```

## Running a Scraper

You can use poetry to run a scraper. The `run` command takes the
scraper function and the url to scrape. The `run_from_file` command
takes the scraper function and the path to the file containing the
urls to scrape.

```shell
poetry run python <path_to_your_file>
```

Happy extraction! 🦍

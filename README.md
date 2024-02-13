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

## Folder Structure
The `scrapers` folder contains all the scrapers. The `harambe` folder
contains the SDK and utility functions.

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
from typing import Any

from playwright.async_api import Page

from harambe import SDK
from harambe import PlaywrightUtils as Pu

SELECTORS = {
    "last_page": "",
    "list_view": "//div[@class='et_pb_blurb_content']",
    "name": "//h4/*[self::span or self::a]",
    "fax": ">Fax.*?strong>(.*?)<br>",
    # etc...
}


# Annotation registers the scraper with the SDK
@SDK.scraper(domain="https://apprhs.org/our-locations/", stage="detail")
async def scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.goto(url)

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
    asyncio.run(SDK.run(scrape, "https://apprhs.org/our-locations/"))
```


#### Listing Scraper
Shown below is an example listing scraper. Use `SDK.enqueue` to to add
urls that will need be scraped by the detail scraper. The `context`
parameter is used to pass data from the listing scraper to the detail
scraper. 

```python
import asyncio
from typing import Any

from playwright.async_api import Page

from harambe import SDK

SELECTORS = {}


@SDK.scraper(domain="https://example.org", stage="listing")
async def scrape(sdk: SDK, url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.goto(url)

    for url in [
        "https://example.org/1",
        "https://example.org/2",
        "https://example.org/3",
    ]:  # Imagine these are locators
        await sdk.enqueue(
            url,
            context={
                "phone": "123-456-7890",
                # Some data from the listing page that we want to pass to the detail page, (optional)
                "foo": "bar",
                "baz": "qux",
            },
        )


@SDK.scraper(domain="https://example.org", stage="detail")
async def scrape_detail(sdk: SDK, url: str, context: Any) -> None:
    page: Page = sdk.page
    await page.goto(url)

    # Grab all properties from the context
    detail = {**context}

    detail["fax"] = "123-456-7890"  # Some data grabbed from the detail page
    detail["type"] = "Hospital"  # Some data grabbed from the detail page
    await sdk.save_data(detail)  # Save the data to the database


if __name__ == "__main__":
    asyncio.run(SDK.run(scrape, "https://navicenthealth.org/locations"))
    asyncio.run(SDK.run_from_file(scrape_detail))
```


## Running a Scraper
You can use poetry to run a scraper. The `run` command takes the
scraper function and the url to scrape. The `run_from_file` command
takes the scraper function and the path to the file containing the
urls to scrape.

```shell
poetry run python poetry run python scrapers/medical/apprhs.py 
```


## Submitting a PR
Before submitting a PR, please run the following commands to ensure
that your code is formatted correctly.

```shell
./format.sh
```

Happy extraction! 🦍
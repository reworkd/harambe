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
- [Example Scraper](#example-scrapers)
  - [Detail Only Scraper](#detail-only-scraper)
  - [Listing Scraper](#listing-scraper)
- [Local Development](#local-development)

---

## Setup and Installation

To install the SDK, run the following command using pip or a package manager of your choice.
```shell
pip install harambe-sdk
```

## Example Scrapers

Generally scrapers come in two types, **listing** and detail **scrapers**. Listing
scrapers are used to collect a list of items to scrape. Detail scrapers
are used to scrape the details of a single item.

If all the items that you want to scrape are available on a single page,
then you can use a detail scraper to scrape all the items. If the
items are spread across multiple pages, then you will need to use a
listing scraper to collect the items and then use a detail scraper to
scrape the details of each item.

#### Detail Only Scraper

Shown below is an example detail scraper. The `context` parameter is
used to pass data from the listing scraper to the detail scraper.
In this example, the `context` parameter is used to pass the phone

```python
import asyncio
from typing import Any

from playwright.async_api import Page

from harambe import SDK

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
from typing import Any

from playwright.async_api import Page

from harambe import SDK


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


if __name__ == "__main__":
  asyncio.run(
    SDK.run(
      listing_scrape,
      "https://kpcode.kp.gov.pk/homepage/list_all_law_and_rule/879351",
      headless=False,
      schema={},
    )
  )
```

## Local Development
Harambe uses [UV](https://docs.astral.sh/uv/getting-started/installation/) for dependency management. 
To get started, clone the repository and install the dependencies using the following commands:

```shell
git clone https://github.com/reworkd/harambe.git
cd harambe/sdk
uv sync
uv run playwright install chromium --with-deps
```

Finally, you can verify that everything is working correctly by running the following command in the
root of the repository directory of the repository:
```shell
./check.sh
```




import sys
sys.path.append('/Users/kunwarsodhi/workspace/harambe')

import asyncio
from typing import Any
from harambe import SDK

from playwright.async_api import Page
from harambe import PlaywrightUtils as Pu

async def scrape(sdk: SDK, current_url: str, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    # Navigate to the iframe's source URL
    await page.goto(
        await Pu.get_attr(page, "//iframe[contains(@src, 'opengov')]", "src")
    )
    while True:
        await sdk.page.wait_for_selector("div.ReactTable")
        # Get all of the desired links to open in new tabs
        link_elements = await sdk.page.query_selector_all("div.ReactTable a")
        for i in range(len(link_elements)):
            await sdk.page.wait_for_selector("div.ReactTable")
            link_elements = await sdk.page.query_selector_all("div.ReactTable a")
            td_elements = await sdk.page.query_selector_all(
                ".rt-td._1lNEVuDlslMqIiKuxGxMFQ"
            )
            status_element = (
                await td_elements[i].query_selector("span._22UYFugF9QpUFCx04p2MJM")
                if td_elements
                else None
            )
            status = await status_element.inner_text() if status_element else None
            if status and ("SOON" in status and "OPEN" not in status):
                continue
            # Listen for the new tab event
            async with page.expect_popup() as popup_info:
                await link_elements[i].click()

            # Get the new tab (popup)
            new_tab = await popup_info.value

            # Wait for content to load in the new tab
            await new_tab.wait_for_selector("#AppContent")

            # Enqueue the new tab's URL
            await sdk.enqueue(new_tab.url)

            # Close the new tab after processing
            await new_tab.close()

        await sdk.page.wait_for_selector(".-next > button")
        next_button = await page.query_selector(".-next > button")
        is_disabled = (
            await next_button.evaluate("button => button.hasAttribute('disabled')")
            if next_button
            else False
        )
        if next_button and not is_disabled:
            await next_button.click()
            await page.wait_for_timeout(5000)
            # await page.wait_for_load_state("networkidle")
        else:
            break

if __name__ == "__main__":
    harness_options = {
        'headers': {
            'x-run-id': '3'
        },
        'proxy': 'http://na:na@127.0.0.1:8080'
    }

    asyncio.run(
        SDK.run(
            scrape,
            "https://www.ppines.com/667/Current-Bids",
            headless=False,
            **harness_options
        )
    )
import asyncio
import os
import re
from typing import Any

from playwright.async_api import Page
from playwright.async_api import TimeoutError

from harambe import SDK


@SDK.scraper(domain="https://www.microchip.com/", stage="detail")
async def scrape(sdk: SDK, url: str, context: Any, *args: Any, **kwargs: Any) -> None:
    page: Page = sdk.page
    await page.goto(url)
    await page.wait_for_selector(
        '//td[contains(text(),"Bid Number")]/following-sibling::td[1][@class="tableText-01"]'
    )
    post_title = await page.locator(
        '//td[contains(text(),"Description:")]/following-sibling::td[1][@class="tableText-01"]'
    ).first.inner_text()
    try:
        await page.wait_for_selector(
            '//td[contains(text(),"Bid Number")]/following-sibling::td[1][@class="tableText-01"]',
            timeout=2000,
        )
        notice_id = await page.locator(
            '//td[contains(text(),"Bid Number")]/following-sibling::td[1][@class="tableText-01"]'
        ).first.inner_text()
    except:
        notice_id = None
    try:
        await page.wait_for_selector(
            '//td[contains(text(),"Bulletin Desc")]/following-sibling::td[1][@class="tableText-01"]',
            timeout=1000,
        )
        desc = await page.locator(
            '//td[contains(text(),"Bulletin Desc")]/following-sibling::td[1][@class="tableText-01"]'
        ).first.inner_text()
        desc = desc.strip()
    except:
        desc = None
    try:
        buyer_agency = await page.locator(
            '//td[contains(text(),"Organization")]/following-sibling::td[1][@class="tableText-01"]'
        ).first.inner_text()
        buyer_agency = buyer_agency.strip()
    except:
        buyer_agency = None
    try:
        buyer_name = await page.wait_for_selector(
            '//td[contains(text(),"Purchaser")]/following-sibling::td[1][@class="tableText-01"]',
            timeout=2000,
        )
        buyer_name = await page.locator(
            '//td[contains(text(),"Purchaser")]/following-sibling::td[1][@class="tableText-01"]'
        ).first.inner_text()
        buyer_name = buyer_name.strip()
    except:
        buyer_name = None
    buyer_data = await page.locator(
        '//td[contains(text(),"Ship-to Address:")]/following-sibling::td[1][@class="tableText-01"]'
    ).first.inner_text()
    email_pattern = r"[\w\.-]+@[\w\.-]+"
    phone_pattern = r"\(\d{3}\)\d{3}-\d{4}"
    emails = re.findall(email_pattern, buyer_data)
    phones = re.findall(phone_pattern, buyer_data)

    if emails:
        buyer_email = emails[0]
    else:
        buyer_email = None
    if phones:
        buyer_phone = phones[0]
    else:
        buyer_phone = None
    try:
        location = await page.locator(
            '//td[contains(text(),"Location")]/following-sibling::td[1][@class="tableText-01"]'
        ).inner_text()
        location = location.strip()
    except:
        location = None
    try:
        await page.wait_for_selector(
            '//td[contains(text(),"Type Code")]/following-sibling::td[1][@class="tableText-01"]',
            timeout=1000,
        )
        typ = await page.locator(
            '//td[contains(text(),"Type Code")]/following-sibling::td[1][@class="tableText-01"]'
        ).inner_text()
        typ = typ.split("-")[-1].strip()
    except:
        typ = None
    # try:
    #     await page.wait_for_selector("//div[contains(text(),'Closed Date')]/following-sibling::div",timeout=1000)
    #     due_date=await page.locator("//div[contains(text(),'Closed Date')]/following-sibling::div").inner_text()
    #     due_date=due_date.strip()
    # except:due_date=None
    try:
        await page.wait_for_selector(
            '//td[contains(text(),"Bid Opening Date")]/following-sibling::td[1][@class="tableText-01"]',
            timeout=1000,
        )
        open_date = await page.locator(
            '//td[contains(text(),"Bid Opening Date")]/following-sibling::td[1][@class="tableText-01"]'
        ).inner_text()
        open_date = open_date.strip()
    except:
        open_date = None
    # try:
    #     await page.wait_for_selector("//div[contains(text(),'NIGP Code')]/following-sibling::div",timeout=1000)
    #     categories=await page.locator("//div[contains(text(),'NIGP Code')]/following-sibling::div").inner_text()
    #     category='\n'
    #     categories=categories.split('\n')
    #     for cat in categories:
    #         category+= cat.split(' ',1)[-1].strip()+'\n'
    #     category=category.strip()
    # except:category=None
    files = []
    for link in await page.query_selector_all(
        '//td[contains(text(),"File Attachments")]/following-sibling::td//a'
    ):
        download_meta = await sdk.capture_download(link)

        files.append({"title": download_meta["filename"], "url": download_meta["url"]})

    await sdk.save_data(
        {
            "id": notice_id,
            "title": post_title,
            "description": desc,
            "location": location,
            "type": typ,
            "category": None,
            "posted_date": open_date,
            "due_date": None,
            "buyer_name": buyer_agency,
            "buyer_contact_name": buyer_name,
            "buyer_contact_number": buyer_phone,
            "buyer_contact_email": buyer_email,
            "attachments": files,
        }
    )


@SDK.scraper(domain="https://www.microchip.com/", stage="detail")
async def scrape2(sdk: SDK, url: str, context: Any, *args: Any, **kwargs: Any) -> None:
    await sdk.page.goto(url)
    download_info = await sdk.capture_pdf()
    await sdk.save_data({"document_url": download_info})
    pdf_path = os.path.expanduser('~/Downloads/good_pdf.pdf')
    # await sdk.page.emulate_media(media="screen")
    await sdk.page.pdf(path=pdf_path)


@SDK.scraper(domain="https://www.microchip.com/", stage="detail")
async def scrape3(sdk: SDK, current_url: str, *args: Any, **kwargs: Any) -> None:
    print("starting")
    await sdk.page.wait_for_selector('.SiteBreadcrumb li.active')
    print("waited for selector")
    original_title = await sdk.page.locator('div.SiteBreadcrumb li.active').inner_text()

    try:
        print("Trying shit")
        # Sometimes its an alert dialog that the doc is way too large
        href = await sdk.page.locator('.EurlexContent .alert a').get_attribute('href', timeout=5000)
        await sdk.save_data({"title": original_title, "document_url": href})
    except TimeoutError:
        print("not alert")
        # Other times its a list of documents
        # Use same original title but append index nubmers
        links = await sdk.page.locator('.EurlexContent ul.multiStreams > li > a').all()
        for i, link in enumerate(links):
            href = await link.get_attribute('href')
            await sdk.save_data({"title": f"{original_title}-{str(i + 1)}", "document_url": href})

        if len(links) == 0:
            print("not links")
            # First go by country
            index_priorities = [
                8,  # English
                9,  # French
                2,  # Spanish
                5,  # Deutsch
                12,  # Italian
            ]
            doc_formats = ['PubFormatPDF', 'PubFormatHTML']

            for index in index_priorities:
                print("found index properties")
                for doc_format in doc_formats:
                    print(doc_format)
                    try:
                        list_item = sdk.page.locator(f'ul.{doc_format} > li:nth-child({index})')
                        # Check it doesn't have disabled class
                        item_class = await list_item.get_attribute('class', timeout=1000)
                        if item_class and "disabled" in item_class:
                            continue

                        await sdk.save_data(
                            {
                                "title": original_title,
                                "document_url": await list_item.locator('a').first.get_attribute('href'),
                            }
                        )
                        return
                    except TimeoutError:
                        continue

            # If no priority document was found, try any language
            try:
                print("Tryung language")
                href = await sdk.page.locator('ul.PubFormatPDF > li:not(.disabled) > a').first.get_attribute('href',
                                                                                                             timeout=5000)
            except TimeoutError:
                print("Tryung html")
                href = await sdk.page.locator('ul.PubFormatHTML > li:not(.disabled) > a').first.get_attribute('href',
                                                                                                              timeout=5000)
            await sdk.save_data({"title": original_title, "document_url": href})


async def scrape5(sdk: Any, current_url: str, context: Any, *args: Any, **kwargs: Any) -> None:
    await sdk.page.wait_for_selector('.SiteBreadcrumb li.active')
    original_title = await sdk.page.locator('div.SiteBreadcrumb li.active').inner_text()

    try:
        # Sometimes its an alert dialog that the doc is way too large
        href = await sdk.page.locator('.EurlexContent .alert a').get_attribute('href', timeout=5000)
        await sdk.save_data({"title": original_title, "document_url": href})
    except TimeoutError:
        # Other times its a list of documents
        # Use same original title but append index nubmers
        links = await sdk.page.locator('.EurlexContent ul.multiStreams > li a').all()
        for i, link in enumerate(links):
            href = await link.get_attribute('href')
            await sdk.save_data({"title": f"{original_title}-{str(i + 1)}", "document_url": href})

        if len(links) == 0:
            original_title = await sdk.page.locator('.DocumentTitle').inner_text()
            # First go by country
            index_priorities = [
                8,  # English
                9,  # French
                2,  # Spanish
                5,  # Deutsch
                12,  # Italian
            ]
            doc_formats = ['PubFormatPDF', 'PubFormatHTML']

            for index in index_priorities:
                for doc_format in doc_formats:
                    try:
                        list_item = sdk.page.locator(f'ul.{doc_format} > li:nth-child({index})')
                        # Check it doesn't have disabled class
                        item_class = await list_item.get_attribute('class')
                        if item_class and "disabled" in item_class:
                            continue

                        await sdk.save_data(
                            {
                                "title": original_title,
                                "document_url": await list_item.locator('a').first.get_attribute('href'),
                            }
                        )
                        return
                    except TimeoutError:
                        continue

            # If no priority document was found, try any language
            try:
                href = await sdk.page.locator('ul.PubFormatPDF > li:not(.disabled) > a').first.get_attribute('href',
                                                                                                             timeout=5000)
            except TimeoutError:
                href = await sdk.page.locator('ul.PubFormatHTML > li:not(.disabled) > a').first.get_attribute('href',
                                                                                                              timeout=5000)
            await sdk.save_data({"title": original_title, "document_url": href})



if __name__ == "__main__":
    asyncio.run(
        SDK.run(
            # scrape,
            # scrape2,
            # scrape3,
            scrape3,
            # "https://www.bidbuy.illinois.gov/bso/external/bidDetail.sdo?docId=23-444DHS-MIS44-B-34703&external=true&parentUrl=close",
            # "https://www.nwc.com.sa/En/MediaCenter/News/Pages/Najran-Prince-launches-7-water.aspx",
            # "https://hands.ehawaii.gov/hands/opportunities/opportunity-details/23953",
            # "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32021R0023&qid=1710506349939",
            # "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=PI_COM:C(2017)8238",
            "https://eur-lex.europa.eu/legal-content/AUTO/?uri=CELEX:32001R1262R(02)&qid=1710506349939&rid=2290",
            # "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R1447R%2803%29&qid=1710506349939",
            # "https://eur-lex.europa.eu/search.html?scope=EURLEX&text=Oljekrisn%C3%A4mnden&lang=en&type=quick&qid=1699865369591",
            # "https://www.mofa.gov.qa/en/all-mofa-news/details/1445/08/22/prime-minister-and-minister-of-foreign-affairs-chairs-gcc-morocco-meeting",
        )
    )
    asyncio.run(SDK.run_from_file(scrape, headless=False))

import asyncio
from datetime import date
import re
from playwright.async_api import async_playwright
import urllib
import json

# scroll to the bottom of the bussines listings or when the limit is reached
async def scroll_to_bottom(page, scroll_selector: str, parent_selector: str, limit : int, scroll_method: str = 'scrollBy(0, 2000)'):
    previous_child_count = 0
    no_new_child_count = 0
    
    while no_new_child_count < 5:
        # Scroll the element
        await page.evaluate(f'''{scroll_selector}.{scroll_method}''')
        await asyncio.sleep(2)  # Wait for new elements to load
        
        # Get the current number of children
        current_child_count = await page.evaluate(f'''{parent_selector}.children.length''')
        
        if current_child_count > limit + 2: # break the loop if the number of element exceeds the limit
            break

        if current_child_count > previous_child_count:
            no_new_child_count = 0  # Reset the count if new children are loaded
        else:
            no_new_child_count += 1  # Increment if no new children are found
            
        previous_child_count = current_child_count

#get the links of all bussiness thah willbe scraped
async def scrape_links(query : str):
    encoded_query = urllib.parse.quote_plus(query)
    url = f'https://www.google.com/maps/search/{encoded_query}'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await scroll_to_bottom(page, 
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     50)
        bussines_elements = await page.query_selector_all("div[role = 'feed'] > div > div > a")
        bussines_links = [await x.get_attribute('href') for x in bussines_elements]
        return bussines_links

async def scrape_data_from_link(url):
    id = re.findall(r'\/data.*\?', url)[0].replace('/data=', '').replace('?', '')
    # print(id)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        # await asyncio.sleep(2)

        titleEl = await page.query_selector('h1')
        title = await titleEl.inner_text() if titleEl else None

        ratingEls = await page.query_selector_all('div.F7nice > span')
        rating = (await ratingEls[0].inner_text()).replace(",", ".") if ratingEls else None
        nratings = (await ratingEls[1].inner_text()).replace("(", "").replace(")", "").replace(".", "") if ratingEls else None

        websiteEl = await page.query_selector("a[data-item-id='authority']")
        website = await websiteEl.inner_text() if websiteEl else None

        phoneEl = await page.query_selector("xpath=//button[starts-with(@data-item-id,'phone')]")
        phone = (await phoneEl.get_attribute('data-item-id')).replace("phone:tel:", "") if phoneEl else None

        categoryEl = await page.query_selector('button.DkEaL')
        category = await categoryEl.inner_text() if categoryEl else None

        # print(website, title, rating, nratings, phone, category)

        hoursEls = await page.query_selector_all("tbody > tr > td[role = 'text']")
        hours = [await hour.get_attribute('aria-label') for hour in hoursEls] if hoursEls else None

        if hours and len(hours) == 7:
            for i in range(7 - date.today().weekday()):
                fr = hours.pop(0)
                hours.append(fr)

        # print(hours)

        res = dict(
            gm_id = id,
            gm_url = url,
            title = title,
            rating = dict(
                stars = float(rating),
                amount = int(nratings)
            ) if rating and nratings else None, 
            category = category,
            website = website,
            phone = phone,
            hours = hours
        )

        with open(f'./test/{title}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(res, ensure_ascii=False))
        
        print(res)

async def scrape_data(query_str : str):
    links = await scrape_links(query_str)
    tasks = []
    for i in range(len(links)):
        tasks.append(scrape_data_from_link(links[i]))
        if (i % 3) == 0:
            await asyncio.gather(*tasks)
            print("Done 3")
            tasks = []
    # tasks = [scrape_data_from_link(url) for url in links]
    # await asyncio.gather(*tasks)
    print("Done All")
    input()

# Entry point to run the scraping tasks
if __name__ == '__main__':
    # asyncio.run(scrape_data_from_link('''https://www.google.com/maps/place/%D0%9A%D0%BB%D1%83%D0%B1-%D0%B8%D0%B3%D1%80%D0%B0%D0%BE%D0%BD%D0%B8%D1%86%D0%B0+%D0%A1%D1%86%D0%B5%D0%BD%D0%B0/data=!4m7!3m6!1s0x475a6f7011a9a6bd:0xb23dcdb3b0a58330!8m2!3d44.8093256!4d20.3805368!16s%2Fg%2F11bw2hqg1n!19sChIJvaapEXBvWkcRMIOlsLPNPbI?authuser=0&hl=sr&rclk=1'''))
    asyncio.run(scrape_data('Perionica u beogradu'))
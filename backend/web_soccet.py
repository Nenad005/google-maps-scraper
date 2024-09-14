import asyncio
from datetime import date
import re
from playwright.async_api import async_playwright
import urllib
from tinydb import TinyDB, Query

db = TinyDB('db.json')
Lead = Query()

async def insert_lead(id: str, gm_url: str, title: str, rating: dict | None, category: str | None, website: str | None, phone: str | None, hours : list | None):
    lead = db.search(Lead.id == id)
    try:
        if lead:
            db.update({'title': title, 'rating' : rating, 'category': category, 'website': website, 'phone': phone, 'hours': hours}, Lead.id == id)
            return 1
        else:
            db.insert({'id': id, 'gm_url': gm_url, 'title': title, 'rating': rating, 'category': category, 'website': website, 'phone': phone, 'hours': hours, 'status': 'idle'})
            return 0
    except Exception as e:
        print(e)
        return -1

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
async def scrape_links(query : str, limit : int):
    encoded_query = urllib.parse.quote_plus(query)
    url = f'https://www.google.com/maps/search/{encoded_query}'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await scroll_to_bottom(page, 
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     limit)
        bussines_elements = await page.query_selector_all("div[role = 'feed'] > div > div > a")
        bussines_links = [await x.get_attribute('href') for x in bussines_elements]
        return bussines_links

async def scrape_data_from_link(url, browser):
    id = re.findall(r'\/data.*\?', url)[0].replace('/data=', '').replace('?', '')

    page = await browser.new_page()
    await page.goto(url)
    
    titleEl = await page.query_selector('h1')
    title = await titleEl.inner_text() if titleEl else None
    if not title:
        return -1

    ratingEls = await page.query_selector_all('div.F7nice > span')
    rating = (await ratingEls[0].inner_text()).replace(",", ".") if ratingEls else None
    nratings = (await ratingEls[1].inner_text()).replace("(", "").replace(")", "").replace(".", "") if ratingEls else None

    websiteEl = await page.query_selector("a[data-item-id='authority']")
    website = await websiteEl.get_attribute('href') if websiteEl else None

    phoneEl = await page.query_selector("xpath=//button[starts-with(@data-item-id,'phone')]")
    phone = (await phoneEl.get_attribute('data-item-id')).replace("phone:tel:", "") if phoneEl else None

    categoryEl = await page.query_selector('button.DkEaL')
    category = await categoryEl.inner_text() if categoryEl else None

    hoursEls = await page.query_selector_all("tbody > tr > td[role='text']")
    hours = [await hour.get_attribute('aria-label') for hour in hoursEls] if hoursEls else None

    if hours and len(hours) == 7:
        for i in range(7 - date.today().weekday()):
            fr = hours.pop(0)
            hours.append(fr)

    status = await insert_lead(
        id=id,
        gm_url=url,
        title=title,
        rating=dict(
            stars=float(rating),
            amount=int(nratings)
        ) if rating and nratings else None,
        category=category,
        website=website,
        phone=phone,
        hours=hours,
    )

    if status == 0:
        print(f"[DONE] - Inserted {title}")
    if status == 1:
        print(f"[DONE] - Updated {title}")
    if status == -1:
        return status

    await page.close()
    return 0

async def scrape_data(query_str: str, limit : int):
    links = await scrape_links(query_str, limit)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        batch_size = 10  # Control the number of simultaneous tasks
        # results = []

        for i in range(0, len(links), batch_size):
            tasks = [scrape_data_from_link(links[j], browser) for j in range(i, min(i + batch_size, len(links)))]
            # results.extend(await asyncio.gather(*tasks))
            await asyncio.gather(*tasks)

        await browser.close()
        # with open("result.json", 'w', encoding="utf-8") as f:
        #     f.write(json.dumps(results, indent=4, ensure_ascii=False))

# Entry point to run the scraping tasks
if __name__ == '__main__':
    query = input("Search query : ")
    limit = int(input("Limit results : "))
    asyncio.run(scrape_data(query, limit))
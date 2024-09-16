import asyncio
from datetime import date
import re
from flask import Flask, Response
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import urllib
from tinydb import TinyDB, Query
db = TinyDB('db.json')
Lead = Query()
app = Flask(__name__)

def insert_lead(id: str, gm_url: str, title: str, rating: dict | None, category: str | None, website: str | None, phone: str | None, hours : list | None):
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
def scroll_to_bottom(page, scroll_selector: str, parent_selector: str, limit : int, scroll_method: str = 'scrollBy(0, 2000)'):
    previous_child_count = 0
    no_new_child_count = 0
    
    while no_new_child_count < 5:
        # Scroll the element
        page.evaluate(f'''{scroll_selector}.{scroll_method}''')
        asyncio.sleep(2)  # Wait for new elements to load
        
        # Get the current number of children
        current_child_count = page.evaluate(f'''{parent_selector}.children.length''')
        
        if current_child_count > limit + 2: # break the loop if the number of element exceeds the limit
            break

        if current_child_count > previous_child_count:
            no_new_child_count = 0  # Reset the count if new children are loaded
        else:
            no_new_child_count += 1  # Increment if no new children are found
            
        previous_child_count = current_child_count

def scrape_data_from_link(url, browser):
    id = re.findall(r'\/data.*\?', url)[0].replace('/data=', '').replace('?', '')

    page = browser.new_page()
    page.goto(url)
    
    titleEl = page.query_selector('h1')
    title = titleEl.inner_text() if titleEl else None
    if not title:
        return -1

    ratingEls = page.query_selector_all('div.F7nice > span')
    rating = (ratingEls[0].inner_text()).replace(",", ".") if ratingEls else None
    nratings = (ratingEls[1].inner_text()).replace("(", "").replace(")", "").replace(".", "") if ratingEls else None

    websiteEl = page.query_selector("a[data-item-id='authority']")
    website = websiteEl.get_attribute('href') if websiteEl else None

    phoneEl = page.query_selector("xpath=//button[starts-with(@data-item-id,'phone')]")
    phone = (phoneEl.get_attribute('data-item-id')).replace("phone:tel:", "") if phoneEl else None

    categoryEl = page.query_selector('button.DkEaL')
    category = categoryEl.inner_text() if categoryEl else None

    hoursEls = page.query_selector_all("tbody > tr > td[role='text']")
    hours = [hour.get_attribute('aria-label') for hour in hoursEls] if hoursEls else None

    if hours and len(hours) == 7:
        for i in range(7 - date.today().weekday()):
            fr = hours.pop(0)
            hours.append(fr)

    status = insert_lead(
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
        # return (f"[DONE] - Inserted {title}")
    if status == 1:
        print(f"[DONE] - Updated {title}")
        # return (f"[DONE] - Updated {title}")
    if status == -1:
        return status

    page.close()
    return 0

def scrape_data_from_el(el, page):
    url = el.get_attribute('href')
    id = re.findall(r'\/data.*\?', url)[0].replace('/data=', '').replace('?', '')

    el.click()

    # input()
    
    titleEl = page.query_selector_all('h1')
    title = titleEl[-1].inner_text() if titleEl else None
    if (title == 'спонѕорисано'):
        input()
    if not title:
        return -1

    ratingEls = page.query_selector_all('div.F7nice > span')
    rating = (ratingEls[0].inner_text()).replace(",", ".") if ratingEls else None
    nratings = (ratingEls[1].inner_text()).replace("(", "").replace(")", "").replace(".", "") if ratingEls else None

    websiteEl = page.query_selector("a[data-item-id='authority']")
    website = websiteEl.get_attribute('href') if websiteEl else None

    phoneEl = page.query_selector("xpath=//button[starts-with(@data-item-id,'phone')]")
    phone = (phoneEl.get_attribute('data-item-id')).replace("phone:tel:", "") if phoneEl else None

    categoryEl = page.query_selector('button.DkEaL')
    category = categoryEl.inner_text() if categoryEl else None

    hoursEls = page.query_selector_all("tbody > tr > td[role='text']")
    hours = [hour.get_attribute('aria-label') for hour in hoursEls] if hoursEls else None

    if hours and len(hours) == 7:
        for i in range(7 - date.today().weekday()):
            fr = hours.pop(0)
            hours.append(fr)

    status = insert_lead(
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
        return f"[DONE] - Inserted {title}"
    if status == 1:
        print(f"[DONE] - Updated {title}")
        return f"[DONE] - Updated {title}"
    if status == -1:
        print(f"[ERROR] - Error on {title}")
        return f"[ERROR] - Error on {title}"

    page.close()
    return 0

def scrape_data(query_str: str, limit : int):
    encoded_query = urllib.parse.quote_plus(query_str)
    url = f'https://www.google.com/maps/search/{encoded_query}'
    yield f"data: Strating the scraper . . .\n"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        scroll_to_bottom(page, 
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
                     limit)
        input()
        bussines_elements = page.query_selector_all("div[role = 'feed'] > div > div > a")
        bussines_links = [x.get_attribute('href') for x in bussines_elements]

        yield f"data: Scraped links : {bussines_links}\n"
        for el in bussines_elements:
            yield f'data: {scrape_data_from_el(el, page)}'

        browser.close()

@app.route('/scrape')
def scrape():
    return Response(scrape_data('Perionica u beograd', 100), mimetype='text/event-stream')


# Entry point to run the scraping tasks
if __name__ == '__main__':
    # query = input("Search query : ")
    # limit = int(input("Limit results : "))
    # asyncio.run(scrape_data(query, limit))
    app.run(debug=True)

import asyncio
import os
import re
import urllib.parse
from datetime import date
from tinydb import TinyDB, Query

# Configurable database path relative to this script
DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')
db = TinyDB(DB_PATH)
Lead = Query()

# Mutex to protect parallel writes to TinyDB file
db_lock = asyncio.Lock()

def cyrillic_to_latin(text, osisana=False):
    if not text:
        return text
    transliteration_map = {
        '\u0410': 'A', '\u0411': 'B', '\u0412': 'V', '\u0413': 'G', '\u0414': 'D', '\u0402': 'Đ',
        '\u0415': 'E', '\u0416': 'Ž', '\u0417': 'Z', '\u0418': 'I', '\u0408': 'J', '\u041A': 'K',
        '\u041B': 'L', '\u0409': 'Lj', '\u041C': 'M', '\u041D': 'N', '\u040A': 'Nj', '\u041E': 'O',
        '\u041F': 'P', '\u0420': 'R', '\u0421': 'S', '\u0428': 'Š', '\u0422': 'T', '\u040B': 'Ć',
        '\u0423': 'U', '\u0424': 'F', '\u0425': 'H', '\u0426': 'C', '\u0427': 'Č', '\u040F': 'Dž',

        '\u0430': 'a', '\u0431': 'b', '\u0432': 'v', '\u0433': 'g', '\u0434': 'd', '\u0452': 'đ',
        '\u0435': 'e', '\u0436': 'ž', '\u0437': 'z', '\u0438': 'i', '\u0458': 'j', '\u043A': 'k',
        '\u043B': 'l', '\u0459': 'lj', '\u043C': 'm', '\u043D': 'n', '\u045A': 'nj', '\u043E': 'o',
        '\u043F': 'p', '\u0440': 'r', '\u0441': 's', '\u0448': 'š', '\u0442': 't', '\u045B': 'ć',
        '\u0443': 'u', '\u0444': 'f', '\u0445': 'h', '\u0446': 'c', '\u0447': 'č', '\u045F': 'dž',
    }
    osisana_transliteration_map = {
        '\u0410': 'A', '\u0411': 'B', '\u0412': 'V', '\u0413': 'G', '\u0414': 'D', '\u0402': 'Dj',
        '\u0415': 'E', '\u0416': 'Z', '\u0417': 'Z', '\u0418': 'I', '\u0408': 'J', '\u041A': 'K',
        '\u041B': 'L', '\u0409': 'Lj', '\u041C': 'M', '\u041D': 'N', '\u040A': 'Nj', '\u041E': 'O',
        '\u041F': 'P', '\u0420': 'R', '\u0421': 'S', '\u0428': 'S', '\u0422': 'T', '\u040B': 'C',
        '\u0423': 'U', '\u0424': 'F', '\u0425': 'H', '\u0426': 'C', '\u0427': 'C', '\u040F': 'Dz',

        '\u0430': 'a', '\u0431': 'b', '\u0432': 'v', '\u0433': 'g', '\u0434': 'd', '\u0452': 'dj',
        '\u0435': 'e', '\u0436': 'z', '\u0437': 'z', '\u0438': 'i', '\u0458': 'j', '\u043A': 'k',
        '\u043B': 'l', '\u0459': 'lj', '\u043C': 'm', '\u043D': 'n', '\u045A': 'nj', '\u043E': 'o',
        '\u043F': 'p', '\u0440': 'r', '\u0441': 's', '\u0448': 's', '\u0442': 't', '\u045B': 'c',
        '\u0443': 'u', '\u0444': 'f', '\u0445': 'h', '\u0446': 'c', '\u0447': 'c', '\u045F': 'dz',
    }
    if not osisana:
        return ''.join(transliteration_map.get(char, char) for char in text)
    return ''.join(osisana_transliteration_map.get(char, char) for char in text)

async def insert_lead(id: str, gm_url: str, title: str, rating: dict | None, category: str | None, website: str | None, phone: str | None, hours: list | None):
    # Ensure transliteration of Cyrillic categories
    if category:
        category = cyrillic_to_latin(category)

    async with db_lock:
        lead = db.search(Lead.id == id)
        try:
            if lead:
                db.update({
                    'title': title,
                    'rating': rating,
                    'category': category,
                    'website': website,
                    'phone': phone,
                    'hours': hours
                }, Lead.id == id)
                return 1
            else:
                db.insert({
                    'id': id,
                    'gm_url': gm_url,
                    'title': title,
                    'rating': rating,
                    'category': category,
                    'website': website,
                    'phone': phone,
                    'hours': hours,
                    'status': 'idle'
                })
                return 0
        except Exception as e:
            print(f"Error writing to TinyDB: {e}")
            return -1

async def scroll_to_bottom(page, scroll_selector: str, parent_selector: str, limit: int, scroll_method: str = 'scrollBy(0, 2000)'):
    previous_child_count = 0
    no_new_child_count = 0
    
    while no_new_child_count < 5:
        # Scroll the element safely
        await page.evaluate(f'''
            const el = {scroll_selector};
            if (el) {{ el.{scroll_method}; }}
        ''')
        await asyncio.sleep(2)  # Wait for new elements to load
        
        # Get the current number of children safely
        current_child_count = await page.evaluate(f'''
            const el = {parent_selector};
            el ? el.children.length : 0
        ''')
        
        if current_child_count > limit + 2:
            break

        if current_child_count > previous_child_count:
            no_new_child_count = 0
        else:
            no_new_child_count += 1
            
        previous_child_count = current_child_count

async def scrape_links(query: str, limit: int, headless: bool = True):
    encoded_query = urllib.parse.quote_plus(query)
    url = f'https://www.google.com/maps/search/{encoded_query}'

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url)
        
        # Wait for either the search feed container to load, or the main selector
        try:
            await page.wait_for_selector("div[role='feed']", timeout=10000)
        except Exception:
            pass

        await scroll_to_bottom(
            page, 
            'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
            'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
            limit
        )
        
        business_elements = await page.query_selector_all("div[role='feed'] > div > div > a")
        business_links = []
        for x in business_elements:
            href = await x.get_attribute('href')
            if href:
                business_links.append(href)
        
        await browser.close()
        return business_links[:limit]

async def scrape_data_from_link(url: str, browser) -> str:
    try:
        # Extract id from Google Maps URL format safely
        match = re.findall(r'\/data.*\?', url)
        if not match:
            return f"[ERROR] - Could not parse URL data: {url}"
        
        id = match[0].replace('/data=', '').replace('?', '')
        page = await browser.new_page()
        
        # Open Google Maps detail page
        await page.goto(url, timeout=30000)
        
        title_el = await page.query_selector('h1')
        title = await title_el.inner_text() if title_el else None
        if not title:
            await page.close()
            return f"[ERROR] - Title not found for: {url}"

        rating_els = await page.query_selector_all('div.F7nice > span')
        rating = None
        nratings = None
        if rating_els and len(rating_els) >= 2:
            try:
                rating = (await rating_els[0].inner_text()).replace(",", ".")
                nratings = (await rating_els[1].inner_text()).replace("(", "").replace(")", "").replace(".", "")
            except Exception:
                pass

        website_el = await page.query_selector("a[data-item-id='authority']")
        website = await website_el.get_attribute('href') if website_el else None

        phone_el = await page.query_selector("xpath=//button[starts-with(@data-item-id,'phone')]")
        phone = None
        if phone_el:
            phone_attr = await phone_el.get_attribute('data-item-id')
            if phone_attr:
                phone = phone_attr.replace("phone:tel:", "")

        category_el = await page.query_selector('button.DkEaL')
        category = await category_el.inner_text() if category_el else None

        hours_els = await page.query_selector_all("tbody > tr > td[role='text']")
        hours = [await hour.get_attribute('aria-label') for hour in hours_els] if hours_els else None

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

        await page.close()

        if status == 0:
            return f"[DONE] - Inserted {title}"
        elif status == 1:
            return f"[DONE] - Updated {title}"
        else:
            return f"[ERROR] - Failed to write database for {title}"
            
    except Exception as e:
        return f"[ERROR] - Exception scraping link {url}: {str(e)}"

async def scrape_data(query_str: str, limit: int, headless: bool = True):
    yield f"data: Starting the scraper for '{query_str}' (limit {limit})...\n"
    try:
        links = await scrape_links(query_str, limit, headless=headless)
    except Exception as e:
        yield f"data: [ERROR] - Failed to acquire links: {str(e)}\n"
        return

    yield f"data: Found {len(links)} links to scrape.\n"
    if not links:
        return

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        batch_size = 5  # Reasonable batch size to prevent rate-limits / high resource usage

        for i in range(0, len(links), batch_size):
            batch_links = links[i:i + batch_size]
            tasks = [scrape_data_from_link(link, browser) for link in batch_links]
            for completed in asyncio.as_completed(tasks):
                res = await completed
                yield f"data: {res}\n"

        await browser.close()
    yield "data: Scraper finished successfully!\n"

if __name__ == '__main__':
    # CLI mode
    import sys
    query = input("Search query: ") if len(sys.argv) < 2 else sys.argv[1]
    limit = int(input("Limit results: ")) if len(sys.argv) < 3 else int(sys.argv[2])
    
    async def run_cli():
        async for line in scrape_data(query, limit, headless=False):
            print(line.strip())
            
    asyncio.run(run_cli())

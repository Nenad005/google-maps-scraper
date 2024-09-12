import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import urllib
from datetime import date

# query = input("Search query (ex: Perionica u Novom Beogradu) : ")
query = "igraonica za decu beograd"
f = True

encoded_query = urllib.parse.quote_plus(query)
url = f'https://www.google.com/maps/search/{encoded_query}'

options = Options()
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(executable_path="chromedriver.exe"), options=options)
driver.maximize_window()

def scroll_to_bottom(driver, scrool_selector, parent_selector, scroll_method = 'scrollBy(0, 1000)'):
    previous_child_count = 0
    no_new_child_count = 0
    while (no_new_child_count < 5):
        driver.execute_script(f'''{scrool_selector}.{scroll_method}''')
        time.sleep(2)
        current_child_count = driver.execute_script(f'''return {parent_selector}.children.length''')

        if current_child_count > previous_child_count:
            no_new_child_count = 0
        else:
            no_new_child_count += 1
        previous_child_count = current_child_count

def get_result_links():
    driver.get(url)

    # scroll_to_bottom(driver, 
    #                  'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")',
    #                  'document.querySelector("#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")')
    
    els = driver.find_elements(By.CSS_SELECTOR, "div[role = 'feed'] > div > div > a")
    links = [x.get_attribute('href') for x in els]
    
    return dict(links= links, els = els)

def get_element_or_none(by, selector):
    try:
        return driver.find_element(by, selector)
    except:
        return None
    
def get_elements_or_none(by, selector):
    try:
        return driver.find_elements(by, selector)
    except:
        return None

def get_result_from_link(link, isEl = False):
    global f
    if isEl:
        link.click()
    else:
        driver.get(link)
    if f:
        time.sleep(5)
        f = False
    else:
        time.sleep(1)

    titleEl = get_elements_or_none(By.CSS_SELECTOR, 'h1')
    title = titleEl[1].get_attribute('innerText') if titleEl is not None else None

    ratingEls = driver.find_elements(By.CSS_SELECTOR, 'div.F7nice > span')
    rating = ratingEls[0].get_attribute('innerText').replace(",", ".") if ratingEls is not None else None
    nratings = ratingEls[1].get_attribute('innerText').replace("(", "").replace(")", "").replace(".", "") if ratingEls is not None else None

    websiteEl = get_element_or_none(By.CSS_SELECTOR, "a[data-item-id='authority']")
    website = websiteEl.get_attribute('href') if websiteEl is not None else None

    phoneEl = get_element_or_none(By.XPATH, "//button[starts-with(@data-item-id,'phone')]")
    phone = phoneEl.get_attribute('data-item-id').replace("phone:tel:", "") if phoneEl is not None else None

    print(title, rating, nratings, website, phone)
    hoursEls = get_elements_or_none(By.CSS_SELECTOR, "tbody > tr > td[role = 'text']")
    hours = [hour.get_attribute('aria-label') for hour in hoursEls] if hoursEls is not None else None
    if hours is not None and len(hours) == 7:
        for i in range(7 - date.today().weekday()):
            fr = hours.pop(0)
            hours.append(fr)
    print(hours)

    res = dict(
        title=title,
        rating=rating,
        nratings=nratings,
        website=website,
        phone=phone,
        hours=hours
    )
    # input()

    return res

def get_results_from_links(links, areEls = False):
    reuslts = []
    for link in links:
        reuslts.append(get_result_from_link(link, areEls))
    return reuslts

t = get_result_links()
links = t['links']
els = t['els']

results = get_results_from_links(els, True)


with open('results.json', 'w') as f:
    f.write(json.dumps(results, indent=4))

input()
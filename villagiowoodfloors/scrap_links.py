

import csv, os, re, shutil, time, json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService
from fake_useragent import UserAgent


def get_random_headers():
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.5"
    }
    return headers


def get_chromedrvier_options():
    headers = get_random_headers()
    print(headers)
    # Set Chrome options
    options = Options()
    # options.headless = True
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument("--no-sandbox")
    prefs = {
        "translate_whitelists": {"de":"en"},  # "de" is for German, "en" is for English
        "translate":{"enabled":True}
    }
    options.add_experimental_option("prefs", prefs)
    return options



def scrap_all_uni_links(html):
    
    all_links = []
    soup= BeautifulSoup(html, "html.parser")
    main_div= soup.find("div", {"class": "collection-items"})
    all_divs= main_div.find_all("div", {"class": "collection-item"}) if main_div else []
    print("Found main div", all_divs)
    # print(f"Found {len(all_divs)} divs")
    if all_divs:
        for div in all_divs:
            a_tag= div.find("a", {"class": "collection-item__img-link"}, href=True)
            data= a_tag["href"]
            print(f"\n\n Found link: {data}\n\n")  # Printing the link found
            all_links.append(data)
    
    print(f"Found {len(all_links)} university links") 
    print(json.dumps(all_links, indent=4))

    return all_links



def scrap_second_page():
    # try:
       
        options = get_chromedrvier_options()
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
        all_links_data = []
        links = [
            ["Abruzzo", "https://villagiowoodfloors.com/collections/abruzzo/"],
            ["Andera", "https://villagiowoodfloors.com/collections/andrea/"],
            ["Casa-Bianca", "https://villagiowoodfloors.com/collections/casa-bianca/"],
            ["Collina", "https://villagiowoodfloors.com/collections/collina/"],
            ["Cremona", "https://villagiowoodfloors.com/collections/cremona/"],
            ["Del Mare", "https://villagiowoodfloors.com/collections/del-mare/"],
            ["La Spezia", "https://villagiowoodfloors.com/collections/la-spezia/"],
            ["Latina", "https://villagiowoodfloors.com/collections/latina/"],
            ["Venetto", "https://villagiowoodfloors.com/collections/venetto/"],
            ["Victoria", "https://villagiowoodfloors.com/collections/victoria/"]
        ]

        for index, (name, link) in enumerate(links, start=1):  # Fetching 1 to 59 pages
            print(f"\n\n\n\nPage {index}:\n")
            driver.get(link)

            html = driver.page_source
            all_links_data.append({
                "name": name,
                "links": scrap_all_uni_links(html)  # Scraping links from each page
            })
            print(f"Found {len(all_links_data)} links")
            time.sleep(2)  # Waiting for page to load
        
        with open('links.json', 'w') as outfile:
            json.dump(all_links_data, outfile, indent=4)
            print("Data saved to universities.json")
            print("Scraping completed.")

    # except Exception as e:
    #     print("An error occurred./n/n", e)
    # finally:
    #     print("QUIT WEB DRIVER ______________")
    #     if driver:
    #         driver.quit()



def sysInit():
    scrap_second_page()


sysInit()
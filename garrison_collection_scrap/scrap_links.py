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
    

    data= {
        "name": "",
        "links": []
    }
    soup= BeautifulSoup(html, "html.parser")

    # For Name
    heading= soup.find("h1", {"class": "page-title"})
    data["name"]= heading.text.strip() if heading else ""

    all_links = []

    main_div= soup.find("div", {"class": "products-row"})
    all_divs= main_div.find_all("div", {"class": "product-col"}) if main_div else []
    print("Found main div", all_divs)
    # print(f"Found {len(all_divs)} divs")
    if all_divs:
        for div in all_divs:
            a_tag= div.find("a", href=True)
            link = "https://www.garrisoncollection.com" + a_tag["href"]

            print(f"\n\n Found link: {link}\n\n")  # Printing the link found
            all_links.append(link)
    
    print(f"Found {len(all_links)} university links")
    data["links"]= all_links
    print(json.dumps(all_links, indent=4))

    return data



def scrap_second_page():
    # try:
       
        options = get_chromedrvier_options()
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
        all_links_data = []
        links = [
            "https://www.garrisoncollection.com/collection/allora",
            "https://www.garrisoncollection.com/collection/allora-9",
            "https://www.garrisoncollection.com/collection/allora-herringbone",
            "https://www.garrisoncollection.com/collection/bellagio",
            "https://www.garrisoncollection.com/collection/beverly-hills",
            "https://www.garrisoncollection.com/collection/cantina",
            "https://www.garrisoncollection.com/collection/canyon-crest",
            "https://www.garrisoncollection.com/collection/carolina-classic",
            "https://www.garrisoncollection.com/collection/cliffside",
            "https://www.garrisoncollection.com/collection/competition-buster",
            "https://www.garrisoncollection.com/collection/contractors-choice",
            "https://www.garrisoncollection.com/collection/crystal-valley",
            "https://www.garrisoncollection.com/collection/da-vinci",
            "https://www.garrisoncollection.com/collection/du-bois",
            "https://www.garrisoncollection.com/collection/exotics",
            "https://www.garrisoncollection.com/collection/french-connection",
            "https://www.garrisoncollection.com/collection/g2-distressed",
            "https://www.garrisoncollection.com/collection/g2-smooth",
            "https://www.garrisoncollection.com/collection/gold-label",
            "https://www.garrisoncollection.com/collection/newport",
            "https://www.garrisoncollection.com/collection/private-selection",
            "https://www.garrisoncollection.com/collection/villa-gialla",
            "https://www.garrisoncollection.com/collection/vineyard"
        ]


        for index, link in enumerate(links, start=1):  # Fetching 1 to 59 pages
            print(f"\n\n\n\nPage {index}:\n")
            driver.get(link)

            html = driver.page_source
            all_links_data.append(scrap_all_uni_links(html))
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
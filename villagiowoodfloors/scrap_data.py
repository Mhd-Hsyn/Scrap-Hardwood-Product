

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
    options.headless = True
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
        "description": "",
        "details": {},
        "images": [],

    }
    soup= BeautifulSoup(html, "html.parser")
    
    # For Nmae
    heading= soup.find("h1", {"class": "product_title entry-title"})
    data["name"]= heading.text.strip() if heading else ""

    # For Description
    description_section = soup.find('section', class_='woocommerce-tabs wc-tabs-wrapper')
    data['description'] = description_section.find('p').get_text(strip=True) if description_section else ""
    
    # For Details
    attributes_list = soup.find('ul', class_='collection-item__attributes attributes')
    attributes_dict = {}
    if attributes_list:
        for li in attributes_list.find_all('li'):
            key = li.find('strong').get_text(strip=True).replace(" ", "").replace("-", "_").lower()
            value = li.find('span').get_text(strip=True)
            attributes_dict[key] = value
    
    data["details"] = attributes_dict
    
    # For Images
    ol_tag = soup.find('ol', class_='flex-control-nav flex-control-thumbs')
    # images = [img['src'] for img in ol_tag.find_all('img', src=True) if img.get('src')] if ol_tag else [""]
    data["images"] =[re.sub(r'-(\d+x\d+)\.', '.', img['src']) for img in ol_tag.find_all('img', src=True) if img.get('src')] if ol_tag else []

    print(f"Data: {json.dumps(data, indent=4)}") 

    return data



def scrap_second_page():
    # try:
       
        options = get_chromedrvier_options()
        driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        with open('links.json', 'r') as file:
            links_data = json.load(file)  # Loading links from JSON file

        for index, data in enumerate(links_data, start=1):  # Fetching 1 to 59 pages
            print(f"Page {index}:\n")
            
            name= data.get("name")
            links= data.get("links")
            print("\n\nName: ________", name)
            products= []
            for link in links:
                print(f"\n\n Found link: {link}\n\n")  # Printing the link found
                
                driver.get(link)

                html = driver.page_source
                products.append(scrap_all_uni_links(html))  # Scraping links from each page

        
            with open(f'{name}.json', 'w') as outfile:
                json.dump(
                    {
                        "name": name,
                        "products": products  # Scraping links from each page
                    }, 
                    outfile, indent=4)
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
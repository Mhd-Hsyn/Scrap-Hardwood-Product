

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
        "link": "",
        "description": "",
        "details": {},
        "moduling": [],
        "images": [],

    }
    soup= BeautifulSoup(html, "html.parser")
    
    # For Nmae
    heading= soup.find("h1", {"class": "page-title"})
    data["name"]= heading.text.strip() if heading else ""

    # For Description
    description_section = soup.find('div', {'id':'product-text'})
    data['description'] = description_section.find('article').get_text(strip=True) if description_section else ""
    
    # For Details
    attributes_list = soup.find('div', {"id": "specifications-tablet-desktop"})
    all_atrs = attributes_list.find_all('div', { 'class':'row'}) if attributes_list else []
    attributes_dict = {}
    if attributes_list:
        for atr in all_atrs:
            
            key = atr.find('div', class_='col-md-3')
            key = key.text.strip().replace(" ", "_") if key else ""
            value = atr.find('div', class_='col-md-9')
            value = value.text.strip()
            attributes_dict[key] = value
    
    data["details"] = attributes_dict


    # moduling detail
    attributes_list = soup.find('div', {"id": "mouldings-tablet-desktop"})
    all_atrs = attributes_list.find_all('div', { 'class':'row'}) if attributes_list else []
    my_attributes_list = []
    if attributes_list:
        for atr in all_atrs:
            all_divs= atr.find_all('div')
            row_list =[]
            if all_divs :
                for div in all_divs:
                    img_tag = div.find('img')
                    if img_tag and img_tag.get('src'):
                        row_list.append(img_tag['src'])
                        continue

                    # Extract and clean text if available
                    if div.text and div.text.strip():
                        row_list.append(div.text.strip())

            my_attributes_list.append(row_list)
            
    
    data["moduling"] = my_attributes_list
    
    # For Images
    images= []
    img_ele= soup.find('img', {'class': 'image-gallery-image'})
    if img_ele and img_ele.get('src'):
        images.append(img_ele['src'])

    ol_tag = soup.find('div', {'id':'products-masonry'})
    if ol_tag:
        all_imgs = ol_tag.find_all('img', src=True)
        if all_imgs:
            images.extend([img['src'] for img in all_imgs if img.get('src')])
    
    data["images"] = images

    print(f"Data: {json.dumps(data, indent=4)}") 

    return data



def scrap_second_page():
    # try:

        with open('links.json', 'r') as file:
            links_data = json.load(file)  # Loading links from JSON file

        for index, data in enumerate(links_data, start=1):  # Fetching 1 to 59 pages
            print(f"Page {index}:\n")
            
            name= data.get("name")
            links= data.get("links")
            print("\n\nName: ________", name)
            name = re.sub(r'[^a-zA-Z0-9]', '', name)
            
            for link in links:
                try:
                    with open(f'scrap-data/{name}.json', 'r') as outfile:
                        scraped_data = json.load(outfile)
                        products = scraped_data.get("products", [])
                except FileNotFoundError:
                    products= []
                except Exception as e:
                    products= []

                print(f"\n\n Found link: {link}\n\n")  # Printing the link found
                
                RETRY = True
                while RETRY:
                    try:

                        options = get_chromedrvier_options()
                        driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=options)
                        driver.maximize_window()
                        driver.get(link)

                        html = driver.page_source
                        data = scrap_all_uni_links(html)
                        data['link'] = link
                        products.append(data)  # Scraping links from each page
                        with open(f'scrap-data/{name}.json', 'w') as outfile:
                            json.dump(
                                {
                                    "name": name,
                                    "products": products  # Scraping links from each page
                                }, 
                                outfile, indent=4)
                            print("Data saved to universities.json")
                            print("Scraping completed.")
                            RETRY = False
                            break

                    except Exception as e:
                        print("An error occurred while scraping the page: ", e)
                        RETRY = True
                        time.sleep(5)  # Wait for 5 seconds before retrying

                    finally:
                        RETRY = True
                        print("QUIT WEB DRIVER ______________")
                        if driver:
                            driver.quit()



def sysInit():
    scrap_second_page()


sysInit()
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import csv
import time

service = Service(executable_path=r'C:/Users/shett/Downloads/chromedriver_win32/chromedriver.exe')
options = Options()
options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# driver_path = r"C:/Users/shett/Downloads/chromedriver_win32/chromedriver.exe"

def get_page_content(url):
    driver = webdriver.Chrome()
    # print(driver)
    driver.get(url)
    time.sleep(3) 
    html_content = driver.page_source
    driver.quit()
    return html_content

def extract_product_data(product, category):
    try:

        product_name = product.find('span', class_='sc-a6c4ca6a-0 PYPED').get_text(strip=True)
        print(product_name)

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product.find('a', class_='w-full cursor-pointer')['href']
        # print(product_link)

        img_tag = product.find('img')
        primary_image = img_tag['src'] if img_tag else "No image available"

        original_price_tag = product.find('span', class_='sc-a6c4ca6a-0 ldEUGQ')
        sale_price_tag = product.find('span', class_='sc-a6c4ca6a-0 ccQTLI sc-8020ee44-11 kbHGvj')

        original_price = original_price_tag.get_text(strip=True) if original_price_tag else None
        sale_price = sale_price_tag.get_text(strip=True) if sale_price_tag else None
        print(original_price)
        print(sale_price)

    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://www.bewakoof.com" + product_link,
        'Primary Image': primary_image,
        'Original Price': original_price,
        'Sale Price': sale_price
    }


def extract_detailed_product_info(product_link):
    html_content = get_page_content(product_link)
    soup = BeautifulSoup(html_content, 'html.parser')
    # print(product_link)
    # print(soup)
    
    try:
        description = soup.find('div', class_='sc-c5ad7663-3 ciZBQr')
        print(description)

        sizes_container = soup.find('div', class_='p-3 text-xs')
        print(sizes_container)
        sizes = []

        if sizes_container:
            size_labels = sizes_container.find_all('label')
            for label in size_labels:
                sizes.append(label.get_text(strip=True))

        # print(sizes)
        images_container = soup.find_all('img', class_='image-magnify-none')  
        all_images = [img['src'] for img in images_container if img.has_attr('src')]

    except AttributeError as e:
        print(f"Error extracting detailed product info: {e}")
        return None, [], []

    return description, sizes, all_images


def scrape_products(category_url, category, writer):
    products_data = []
    page_number = 1
    
    while True:
        print(f"Scraping page {page_number} for category: {category}")
        page_url = f"{category_url}?page={page_number}"
        html_content = get_page_content(page_url)
        
        if not html_content:
            print(f"Failed to retrieve page content from {page_url}")
            break
            
        soup = BeautifulSoup(html_content, 'html.parser')

        product_cards = soup.find_all('section', class_='sc-8020ee44-4 eNrzXV')

        if not product_cards:
            print("No more products found on this page.")
            break

        for product in product_cards:
            product_data = extract_product_data(product, category)
            if product_data:
                description, sizes, all_images = extract_detailed_product_info(product_data['Product Link'])
                product_data['Description'] = description
                product_data['Sizes'] = ', '.join(sizes) 
                product_data['All Images'] = ', '.join(all_images) 

                writer.writerow(product_data)

                print(f"Added product: {product_data['Product Name']}")

        page_number += 1  

# Define collection URLs
collection_urls = [
    # {'category': 'sweatshirts', 'url': 'https://bluorng.com/collections/sweatshirts'},
    # {'category': 'polos', 'url': 'https://bluorng.com/collections/polos'},
    # {'category': 'shirts-unisex', 'url': 'https://bluorng.com/collections/shirts-unisex'},
    # {'category': 'jackets', 'url': 'https://bluorng.com/collections/jackets'},
    # {'category': 'hoodies', 'url': 'https://bluorng.com/collections/hoodies'},
    # {'category': 'cargos', 'url': 'https://bluorng.com/collections/cargos'},
    # {'category': 'jeans', 'url': 'https://bluorng.com/collections/jeans'},
    # {'category': 'shorts', 'url': 'https://bluorng.com/collections/shorts'},
    {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-t-shirts'},
    # Add more collections here
]

# Prepare to save data to a CSV file
csv_file = 'bluorng_products.csv'

# Define CSV headers
csv_headers = ['Category', 'Product Name', 'Product Link', 'Primary Image', 'Original Price', 'Sale Price', 'Description', 'Sizes', 'All Images']

# Write data to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

    # Scrape products from all collections
    for collection in collection_urls:
        scrape_products(collection['url'], collection['category'], writer)

print(f"Scraped data has been saved to {csv_file}")

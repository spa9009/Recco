import requests 
from bs4 import BeautifulSoup
import csv
import os

def get_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def extract_product_data(product, category):
    try:

        product_name = product.find('h3', class_='card__heading').get_text(strip=True)

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product.find('a', class_='full-unstyled-link')['href']

        img_tag = product.find('img')
        primary_image = img_tag['src'] if img_tag else "No image available"

        original_price_tag = product.find('span', class_='price-item--regular')
        sale_price_tag = product.find('span', class_='price-item--sale')

        original_price = original_price_tag.get_text(strip=True) if original_price_tag else None
        sale_price = sale_price_tag.get_text(strip=True) if sale_price_tag else None

    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://www.bluorng.com" + product_link,
        'Primary Image': primary_image,
        'Original Price': original_price,
        'Sale Price': sale_price
    }

def extract_detailed_product_info(product_link):
    html_content = get_page_content(product_link)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        description = soup.find('div', class_='product__description rte quick-add-hidden').find('div', class_='product-details-desc').p.get_text(strip=True)

        sizes_container = soup.find('fieldset', class_='js product-form__input')
        sizes = []
        if sizes_container:
            size_inputs = sizes_container.find_all('input', type='radio')
            sizes = [input_tag['value'] for input_tag in size_inputs if input_tag.has_attr('value')]

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

        product_cards = soup.find_all('div', class_='card card--standard card--media')

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
    {'category': 'pants', 'url': 'https://bluorng.com/collections/pants'},
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

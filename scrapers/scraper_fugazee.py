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
        # Extract the product name and link
        product_name = product.find('p', class_='card__title').get_text(strip=True)

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product.find('a', class_='card-link text-current js-prod-link')['href']

        img_tag = product.find('img', class_='img-fit img-fit--contain card__main-image')
        primary_image = img_tag['src'] if img_tag else "No image available"

        original_price_tag = product.find('strong', class_='price__was')
        sale_price_tag = product.find('span', class_='price__current')

        original_price = original_price_tag.get_text(strip=True) if original_price_tag else None
        sale_price = sale_price_tag.get_text(strip=True) if sale_price_tag else None

    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://www.fugazee.com" + product_link,
        'Primary Image': primary_image,
        'Original Price': original_price,
        'Sale Price': sale_price
    }

def extract_product_data(product, category):
    try:
        # Extract the product name and link
        product_name = product.find('p', class_='card__title').get_text(strip=True)

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product.find('a', class_='card-link text-current js-prod-link')['href']

        img_tag = product.find('img', class_='img-fit img-fit--contain card__main-image')
        primary_image = img_tag['src'].lstrip('/') if img_tag else "No image available"

        # Initialize price variables
        original_price = None
        sale_price = None
        
        original_price_tag = product.find('strong', class_='price__was')
        sale_price_tag = product.find('span', class_='price__current')

        if original_price_tag:
            original_price = original_price_tag.get_text(strip=True)
        if sale_price_tag:
            sale_price = sale_price_tag.get_text(strip=True)

    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://www.fugazee.com" + product_link,
        'Primary Image': primary_image,
        'Original Price': original_price,
        'Sale Price': sale_price
    }


from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

def extract_detailed_product_info(product_link):
    html_content = get_page_content(product_link)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        # Adjust the product description selector according to the Fugazee site
        description = soup.find('div', class_='disclosure__panel has-motion').get_text(strip=True)

        # Adjusting the size options selector
        sizes_container = soup.find('div', class_='option-selector__btns flex flex-wrap')
        sizes = []
        if sizes_container:
            size_inputs = sizes_container.find_all('input', type='radio')
            sizes = [input_tag['value'] for input_tag in size_inputs if input_tag.has_attr('value')]

        # Extracting all images from the media gallery container
        images_container = soup.find_all('div', class_='media-gallery__viewer relative')  
        all_images = []
        for img_div in images_container:
            img_tags = img_div.find_all('img')  # Find all img tags in the div
            for img_tag in img_tags:
                if img_tag.has_attr('src'):
                    all_images.append(img_tag['src'].lstrip('/'))  # Collect the src attribute

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

        # Find all product cards using the specified method
        product_cards = soup.find_all("product-card")  # Change this line based on your requirements

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
    {'category': 'crochets', 'url': 'https://www.fugazee.com/collections/crochets'},
    {'category': 't-shirt', 'url': 'https://www.fugazee.com/collections/t-shirt'},
    {'category': 'shirts', 'url': 'https://www.fugazee.com/collections/shirts'},
    {'category': 'oversized-thick-premium-tshirts', 'url': 'https://www.fugazee.com/collections/oversized-thick-premium-tshirts'},
    {'category': 'tracksuits', 'url': 'https://www.fugazee.com/collections/tracksuits'},
    {'category': 'clothing-sets', 'url': 'https://www.fugazee.com/collections/clothing-sets'},
    {'category': 'dungarees-jumpsuits', 'url': 'https://www.fugazee.com/collections/dungarees-jumpsuits'},
    {'category': 'jackets', 'url': 'https://www.fugazee.com/collections/jackets'},
    {'category': 'sweatshirts', 'url': 'https://www.fugazee.com/collections/sweatshirts'},
    {'category': 'sweaters', 'url': 'https://www.fugazee.com/collections/sweaters'},
    {'category': 'overshirt', 'url': 'https://www.fugazee.com/collections/overshirt'},
    {'category': 'shrugs', 'url': 'https://www.fugazee.com/collections/shrugs'},
    {'category': 'trackpants', 'url': 'https://www.fugazee.com/collections/trackpants'},
    {'category': 'jeans', 'url': 'https://www.fugazee.com/collections/jeans'},
    {'category': 'trousers', 'url': 'https://www.fugazee.com/collections/trousers'},
    {'category': 'shorts', 'url': 'https://www.fugazee.com/collections/shorts'},
    {'category': 'unisex', 'url': 'https://www.fugazee.com/collections/unisex'},
    {'category': 'fresh-arrival', 'url': 'https://www.fugazee.com/collections/fresh-arrival'},
]

csv_file = 'fugazee_products.csv'

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

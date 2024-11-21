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
        product_name_tag = product.find('div', class_='break-words')
        product_name = product_name_tag.text.strip() if product_name_tag else "No product name"
        # print(product_name)

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None
        product_link_tag = product.find('a', class_='tile-link absolute inset-0 z-10 group hidden lg:block')
        relative_product_link = product_link_tag.get('href') if product_link_tag else "No link available"
        full_product_link = "https://themangastore.in" + relative_product_link if relative_product_link != "No link available" else None
        # print(full_product_link)
        img_container = product.find('div', class_='group tile-media-wrapper rounded-media rounded-media relative overflow-hidden aspect-css-var')
        img_tag = img_container.find('img') if img_container else None
        primary_image = img_tag['src'].lstrip('//') if img_tag else "No image available"
        # print(primary_image)

        price_container = product.find('div', class_='tile-content-wrapper mt-2')
        price = price_container.select_one('#Section-template--22427452473652__product-grid-Product-9139571523892-label span span').text.strip() if price_container else "No price available"
        # print(price)
    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': full_product_link,
        'Primary Image': primary_image,
        'Price': price,
    }




from bs4 import BeautifulSoup


def extract_detailed_product_info(full_product_link):
    print(f"Running extract_detailed_product_info for product link: {full_product_link}")
    
    html_content = get_page_content(full_product_link)
    if not html_content:
        print(f"Failed to retrieve content for product link: {full_product_link}")
        return 'Description not found.', [], []

    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        
        description_container = soup.find('div', class_='disclosure__panel has-motion')
        description = description_container.text.strip() if description_container else 'Description not found.'
        print(f"Description: {description}")

        sizes_container = soup.find('div', class_='flex flex-wrap gap-2')
        sizes = []
        if sizes_container:
            size_inputs = sizes_container.find_all('input', type='radio')
            sizes = [input_tag['value'] for input_tag in size_inputs if input_tag.has_attr('value')]
        print(f"Sizes: {sizes}")
        images_container = soup.find_all('div', class_='relative overflow-hidden aspect-w-1 aspect-h-1')
        all_images = []
        for container in images_container:
            img_tags = container.find_all('img')
            for img in img_tags:
                if img.has_attr('src'):
                    image_url = img['src'].lstrip('//')
                    all_images.append(image_url)
        print(f"Images: {all_images}")

    except AttributeError as e:
        print(f"Error extracting detailed product info for link {full_product_link}: {e}")
        return 'Description not found.', [], []

    return description, sizes, all_images


import time

def scrape_products(category_url, category, writer):
    page_number = 1
    
    while True:
        print(f"Scraping page {page_number} for category: {category}")
        page_url = f"{category_url}?page={page_number}"
        html_content = get_page_content(page_url)
        
        if not html_content:
            print(f"Failed to retrieve page content from {page_url}")
            break
            
        soup = BeautifulSoup(html_content, 'html.parser')
        product_cards = soup.find_all('li', class_='relative group')

        if not product_cards:
            print("No more products found on this page.")
            break

        for index, product in enumerate(product_cards, start=1):
            print(f"\nProcessing product {index} on page {page_number}")
            product_data = extract_product_data(product, category)
            if product_data and product_data['Product Link']:
                print(f"Extracting detailed info for product: {product_data['Product Name']}")
                time.sleep(2) 

                description, sizes, all_images = extract_detailed_product_info(product_data['Product Link'])
                product_data['Description'] = description
                product_data['Sizes'] = ', '.join(sizes)
                product_data['All Images'] = ', '.join(all_images)

                writer.writerow(product_data)
                print(f"Added product: {product_data['Product Name']}")
            else:
                print(f"Skipping product due to missing data: {product_data}")

        page_number += 1




# Define collection URLs
collection_urls = [
    {'category': 'codered', 'url': 'https://themangastore.in/collections/codered'},
    {'category': 'summer24', 'url': 'https://themangastore.in/collections/summer24'},
    {'category': 'aw23', 'url': 'https://themangastore.in/collections/aw23'},
    {'category': 'ss23', 'url': 'https://themangastore.in/collections/ss23'},
    {'category': 'drop-3-0', 'url': 'https://themangastore.in/collections/drop-3-0'},
    {'category': 'drop-1-0', 'url': 'https://themangastore.in/collections/drop-1-0'},
    {'category': 'basic-not-basic', 'url': 'https://themangastore.in/collections/basic-not-basic'},
]

csv_file = 'fugazee_products.csv'

# Define CSV headers
csv_headers = ['Category', 'Product Name', 'Product Link', 'Primary Image', 'Price', 'Description', 'Sizes', 'All Images']

# Write data to CSV
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

    # Scrape products from all collections
    for collection in collection_urls:
        scrape_products(collection['url'], collection['category'], writer)

print(f"Scraped data has been saved to {csv_file}")

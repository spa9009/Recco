import requests
from bs4 import BeautifulSoup
import csv
import re
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
        product_info = product.find('figcaption')
        product_name = product_info.find('h4').text.strip()

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product_info.find('a').get('href')

        # print(product_link)

        img_tag = product.find('img', class_='product-grid-view_defaultImages__pxr79 defaultimages')
        primary_image = img_tag['srcset'].lstrip('//') if img_tag else "No image available"

        # print(primary_image)

        price = product_info.find('div', class_='price').text.strip()

        # print(price)


    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://www.powerlook.in" + product_link,
        'Primary Image': primary_image,
        'Price': price,
        # 'Sale Price': sale_price_text
    }


from bs4 import BeautifulSoup


def extract_detailed_product_info(product_link):
    html_content = get_page_content(product_link)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        accordian_div = soup.find('div', class_='MoreDetailsSection_accordian__qh3tz')
        # print(accordian_div)

        # Check if the div was found and extract the text
        if accordian_div:
            description = accordian_div.get_text(strip=True)
            print(description)
        else:
            print("The div was not found.")

        
        sizes_container = soup.find('ul', class_='opt-dropdown')
        sizes = []
        if sizes_container:
            size_inputs = sizes_container.find_all('input', type='radio')
            sizes = [input_tag['value'] for input_tag in size_inputs if input_tag.has_attr('value')]
            

        images_container = soup.find('div', class_='styles_sliderContainer__kgtSN')  
        all_images = [img['src'] for img in images_container if img.has_attr('src')]

    except AttributeError as e:
        print(f"Error extracting detailed product info: {e}")
        return None, [], []

    return description, sizes, all_images

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
        product_cards = soup.find_all('div', class_='col-sm-4')

        if not product_cards:
            print("No more products found on this page.")
            break

        for product in product_cards:
            product_data = extract_product_data(product, category)

            # Debugging statement to check product data
            print(f"Extracted product data: {product_data}")

            if product_data:
                description, sizes, all_images = extract_detailed_product_info(product_data['Product Link'])

                # Debugging statement to check detailed product data
                print(f"Detailed Product Info - Description: {description}, Sizes: {sizes}, Images: {all_images}")

                product_data['Description'] = description
                product_data['Sizes'] = ', '.join(sizes)
                product_data['All Images'] = ', '.join(all_images)

                writer.writerow(product_data)
                print(f"Added product: {product_data['Product Name']}")

        page_number += 1  # Increment page number for pagination


# Define collection URLs
collection_urls = [
    {'category': 't-shirts', 'url': 'https://www.powerlook.in/product-category/t-shirts/textured-polos'},
    {'category': 'women-sneakers', 'url': 'https://www.wearcomet.com/collections/women-sneakers'},
    # {'category': 'chunkies', 'url': 'https://7-10.in/collections/chunkies'},
    # {'category': 'chunkies-women', 'url': 'https://7-10.in/collections/chunkies-women'},
    # {'category': 'high-top-women', 'url': 'https://7-10.in/collections/high-top-women'},
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

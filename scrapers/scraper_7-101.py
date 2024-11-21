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
        product_name = product.find('div', class_='grid-product__title').text.strip()

        if product_name == "Hoodie combo (Unisex)":
            print(f"Skipping product: {product_name}")
            return None

        product_link = product.find('a', class_='grid-product__link').get('href')

        img_tag = product.find('img', class_='grid-product__image lazyloaded')
        primary_image = img_tag['src'].lstrip('//') if img_tag else "No image available"

        price_container = product.find('div', class_='grid-product__price')
        original_price = price_container.find('del', class_='grid-product__price--original')
        if original_price:
            original_price_text = original_price.get_text(strip=True)
        else:
            original_price_text = None  # Handle case if there's no original price

        # Extract the sale price
        sale_price = price_container.find('span', class_='sale-price')
        if sale_price:
            sale_price_text = sale_price.get_text(strip=True)
        else:
            sale_price_text = None 
    except AttributeError as e:
        print(f"Error extracting product data: {e}")
        return None

    return {
        'Category': category,
        'Product Name': product_name,
        'Product Link': "https://7-10.in" + product_link,
        'Primary Image': primary_image,
        'Original Price': original_price_text,
        'Sale Price': sale_price_text
    }


from bs4 import BeautifulSoup


def extract_detailed_product_info(product_link):
    print(f"Fetching details for product link: {product_link}")
    html_content = get_page_content(product_link)

    # If no content is returned, skip this product
    if not html_content:
        print(f"Failed to fetch content for product link: {product_link}")
        return 'Description not found.', [], []

    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        # Extract the product description
        description_container = soup.find('div', class_='disclosure__panel has-motion')
        description = description_container.text.strip() if description_container else 'Description not found.'

        # Adjusting the size options selector
        sizes_container = soup.find('fieldset', class_='variant-input-wrap')
        sizes = []
        if sizes_container:
            size_inputs = sizes_container.find_all('input', type='radio')
            sizes = [input_tag['value'] for input_tag in size_inputs if input_tag.has_attr('value')]

        # Extracting images from each product-image-main container
        images_container = soup.find_all('div', class_='product-image-main')
        all_images = []

        for container in images_container:
            img_tags = container.find_all('img')
            for img in img_tags:
                if img.has_attr('src'):
                    image_url = img['src'].lstrip('//')
                    all_images.append(image_url)

        if not all_images:
            print("No images found in the containers.")

    except AttributeError as e:
        print(f"Error extracting detailed product info: {e}")
        return 'Description not found.', [], []

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
        product_cards = soup.find_all('div', class_='grid-product__content')

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
    {'category': 'low-top', 'url': 'https://7-10.in/collections/low-top'},
    {'category': 'high-top', 'url': 'https://7-10.in/collections/high-top'},
    {'category': 'chunkies', 'url': 'https://7-10.in/collections/chunkies'},
    {'category': 'chunkies-women', 'url': 'https://7-10.in/collections/chunkies-women'},
    {'category': 'high-top-women', 'url': 'https://7-10.in/collections/high-top-women'},
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

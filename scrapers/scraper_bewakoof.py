import requests 
from bs4 import BeautifulSoup 
import csv 
import os 
from selenium import webdriver 
import time

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
        product_name = product.find('span', class_='sc-a6c4ca6a-0 PYPED').get_text(strip=True) 
        print(product_name)

        if product_name == "Hoodie combo (Unisex)": 
            print(f"Skipping product: {product_name}") 
            return None

        product_link = product.find('a', class_='w-full cursor-pointer')['href'] 
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
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(product_link)
    
    # Wait for JavaScript to finish loading
    time.sleep(5)  # Adjust this time as needed or use WebDriverWait for dynamic waiting
    
    # Get the page source after JavaScript has rendered
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Close the browser
    driver.quit()
    
    try:
        description_div = soup.find('div', class_='pb-3 font-[familyRegular]')
        print(description_div)
        description = description_div.get_text(strip=True) if description_div else "No description available"
         
        sizes = [] 
        sizes_divs = soup.find_all('div', class_='sc-112b0ace-14 jhxkZq')

        for size_div in sizes_divs:
            label = size_div.find('label')
            if label:
                sizes.append(label.get_text(strip=True))

        all_images = []
        image_divs = soup.find_all('div', class_='swiper-slide')  # Adjust this class as needed

        for image_div in image_divs:
            img_tag = image_div.find('img')
            if img_tag and 'src' in img_tag.attrs:
                all_images.append(img_tag['src'])
                print(all_images)

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
    {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-t-shirts'},
     {'category': 'TopWear', 'subcategory': 'men-printed-tshirts', 'url': 'https://www.bewakoof.com/men-printed-tshirts'}, 
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/oversized-t-shirts-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/classic-t-shirt-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/sweatshirts-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-plain-t-shirts'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/half-sleeve-t-shirts-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/polo-t-shirts-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-shirts'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-full-sleeve-t-shirts'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-co-ord-sets'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-joggers'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/mens-denim'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/baggy-jeans-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/baggy-jeans-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-pajamas'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/cargos-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/cargo-pants-for-men'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-pants'},
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/parachute-pants-for-men'}
     {'category': 'TopWear', 'subcategory': 'mens-tshirts', 'url': 'https://www.bewakoof.com/men-shorts'},https://www.bewakoof.com/men-shorts

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

import requests
from bs4 import BeautifulSoup


# URL of the page to scrape
url = "https://themangastore.in/collections/codered"

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all product containers
    products = soup.find_all('li', class_='relative group')

    # Check if products are found
    if not products:
        print("No products found.")
    else:
        # Iterate over each product and extract the desired information
        for product in products:
            # Extract product title
            title = product.find('div', class_='break-words').text.strip()
            print(title)
            product_link = product.find('a', class_='tile-link absolute inset-0 z-10 group block lg:hidden').get('href')
            print(product_link)
            img_container = product.find('div' , class_='group tile-media-wrapper rounded-media rounded-media relative overflow-hidden  aspect-css-var')
            img_tag = product.find('img')
            primary_image = img_tag['src'].lstrip('//') if img_tag else "No image available"
            print(primary_image)
            # Extract price information
            price_container = product.find('div', class_='tile-content-wrapper mt-2')
            price = price_container.select_one('#Section-template--22427452473652__product-grid-Product-9139571523892-label span span').text.strip()
            print(price)

            # Print the extracted information
            print(f"Title: {title}, Original Price: {price}")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

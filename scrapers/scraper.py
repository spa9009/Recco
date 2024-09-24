import requests
from bs4 import BeautifulSoup
import json

url = "https://www.urbanmonkey.com/collections/tops?page=4"

response = requests.get(url)

if response.status_code == 200 :
    print("Got 200 response from website")
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(json.loads(response.text))
    product_containers = soup.select('div:has(h2), li:has(h2), div:has(img)')
    print(product_containers)
else :
    print("Reponse not 200")
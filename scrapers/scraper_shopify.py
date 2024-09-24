import pandas as pd
import requests as r
from bs4 import BeautifulSoup

url = "https://www.urbanmonkey.com/collections/tops?page=4"

req1 = r.get(url)

soup = BeautifulSoup(req1.text, 'html.parser')

soup.find_all('div', class_='t4s-product gtm-product-card gtm-product-info t4s-pr-grid')
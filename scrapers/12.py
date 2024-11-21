from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

# Visit the page
driver.get("https://www.bewakoof.com/p/mens-black-crest-mark-graphic-printed-oversized-t-shirt")

# Wait for JavaScript to finish loading
time.sleep(5)  # Adjust this time as needed or use WebDriverWait for dynamic waiting

# Get the page source after JavaScript has rendered
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Save the HTML content to a file
with open("page_content.html", "w", encoding="utf-8") as file:
    file.write(soup.prettify())

# Close the browser
driver.quit()

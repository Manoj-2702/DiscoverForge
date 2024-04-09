from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymongo

CONNECTION_STRING = "mongodb://localhost:27017/"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client["Products"]
collection = db["product_info2"]

service = Service("edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service)

driver.get("https://slashdot.org/")
time.sleep(5)

all_element = driver.find_element(By.LINK_TEXT, "Software")
all_element.click()


def scroll_and_scrape():
    last_height = driver.execute_script("return document.body.scrollHeight")
    products = driver.find_elements(By.CSS_SELECTOR, "div.result-heading-texts")
    for product in products:
        try:
        # Extracting product name and description - Adjust selectors as needed
            product_name = product.find_element(By.CSS_SELECTOR, "h3").text
            if collection.count_documents({"name": product_name}, limit=1):
                print(f"Skipping duplicate entry: {product_name}")
                continue
            description = product.find_element(By.CSS_SELECTOR, "div.description").text
            # Insert into MongoDB
            product_doc = {"name": product_name, "description": description}
            collection.insert_one(product_doc)
        except Exception as e:
            print(f"Error extracting product details: {e}")
            continue
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(5)  # Wait for the page to load after scrolling

        # new_height = driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        #     break
        # last_height = new_height

while True:
    scroll_and_scrape()
    time.sleep(5) 
    next_button = driver.find_element(By.LINK_TEXT, "Next")
    next_button.click()

# time.sleep(50)
driver.quit()
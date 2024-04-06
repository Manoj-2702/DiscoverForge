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
collection = db["product_info1"]

service = Service("edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service)

driver.get("https://www.producthunt.com/")

all_element = driver.find_element(By.LINK_TEXT, "All")
all_element.click()

def scroll_and_scrape():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load after scrolling

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        containers = driver.find_elements(By.CSS_SELECTOR, "div.styles_titleItem__bCaNQ")
        
        for container in containers:
            try:
                product_name = container.find_element(By.TAG_NAME, "strong").text
                # Check if the product name already exists in the collection
                if collection.count_documents({"name": product_name}, limit=1):
                    print(f"Skipping duplicate entry: {product_name}")
                    continue

                full_text = container.find_element(By.CSS_SELECTOR, "div.styles_titleTaglineItem__d5Rut").text
                parts = full_text.split("—")
                product_description = parts[1].strip()
                topic_elements = container.find_elements(By.CSS_SELECTOR, "div.styles_underlinedLink__MUPq8, a.styles_underlinedLink__MUPq8")
                topics = [topic.text for topic in topic_elements]
                product_doc = {
                    "name": product_name,
                    "description": product_description,
                    "topics": topics
                }
                collection.insert_one(product_doc)
            except Exception as e:
                print(f"Error encountered for {product_name}: {e}")
                continue
    

scroll_and_scrape()
# time.sleep(50)
driver.quit()
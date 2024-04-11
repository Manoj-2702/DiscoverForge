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
collection = db["product_info3"]

service = Service("edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service)
driver.maximize_window()

driver.get("https://www.sideprojectors.com/#/")
time.sleep(5)

ids = ["input-project-type-blog", "input-project-type-domain", "input-project-type-other"]
clicked = True

for id_value in ids:
    try:
        element = driver.find_element(By.ID, id_value)
        element.click()
        clicked = False
    except:
        continue

search_button=driver.find_element(By.XPATH, '//button[text()="Search"]')
search_button.click()

time.sleep(5)

def scroll_and_scrape():
    last_height = driver.execute_script("return document.body.scrollHeight")
    products = driver.find_elements(By.CSS_SELECTOR, "a.project-item")
    for product in products:
        try:
            product_name = product.find_element(By.CSS_SELECTOR, ".name").text
            # print(product_name)
            if collection.count_documents({"name": product_name}, limit=1):
                print(f"Skipping duplicate entry: {product_name}")
                continue
            description = product.find_element(By.CSS_SELECTOR, "div.description").text
            date_span = product.find_elements(By.CSS_SELECTOR, "div.mt-6.flex.items-center span.gray-text")[-1].text
            product_doc = {"name": product_name, "description": description,"date": date_span}
            collection.insert_one(product_doc)
        except Exception as e:
            # print(f"Error extracting product details: {e}")
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
    next_button = driver.find_element(By.XPATH, '//button[text()="Next"]')
    next_button.click()

time.sleep(5)
driver.quit()


# from selenium import webdriver
# from selenium.webdriver.edge.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pymongo

# CONNECTION_STRING = "mongodb://localhost:27017/"
# client = pymongo.MongoClient(CONNECTION_STRING)
# db = client["Products"]
# collection = db["product_info4"]

# service = Service("edgedriver_win64/msedgedriver.exe")
# driver = webdriver.Edge(service=service)
# driver.maximize_window()

# driver.get("https://www.betalist.com/")
# time.sleep(5)


# topic_button=driver.find_element(By.LINK_TEXT, "Topics")
# topic_button.click()

# time.sleep(5)

# def scroll_and_scrape():
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     containers = driver.find_elements(By.CLASS_NAME, "myContainer")
#     # print(second_container)
#     if len(containers) >= 2:
#         container = containers[2]
#         products=container.find_elements(By.CSS_SELECTOR, "a.flex.items-center")
#         # print(products)
#         for product in products:
#             try:
#                 product_name = product.find_element(By.CSS_SELECTOR, "div.grow.truncate").text
#                 print(product_name)
#                 # if collection.count_documents({"name": product_name}, limit=1):
#                 #     print(f"Skipping duplicate entry: {product_name}")
#                 #     continue
#                 # description = product.find_element(By.CSS_SELECTOR, "div.description").text
#                 # date_span = product.find_elements(By.CSS_SELECTOR, "div.mt-6.flex.items-center span.gray-text")[-1].text
#                 # product_doc = {"name": product_name, "description": description,"date": date_span}
#                 # collection.insert_one(product_doc)
#             except Exception as e:
#                 # print(f"Error extracting product details: {e}")
#                 continue
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(5)  # Wait for the page to load after scrolling

#     new_height = driver.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         return
#     last_height = new_height

# while True:
#     scroll_and_scrape()
#     time.sleep(5) 
# #     next_button = driver.find_element(By.XPATH, '//button[text()="Next"]')
# #     next_button.click()

# time.sleep(5)
# driver.quit()
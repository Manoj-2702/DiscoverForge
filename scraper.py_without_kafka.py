from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
from kafka import KafkaProducer
load_dotenv()
TWITTER_USER_NAME=os.getenv("TWITTER_USER_NAME")
TWITTER_PASSWORD=os.getenv("TWITTER_PASSWORD")

def setup_webdriver():
    # chrome_options = Options()   
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

def scrape_twitter(producer):
    driver = setup_webdriver()
    def extract_tweets(driver, search_text):
        search_input = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='SearchBox_Search_Input']")))
        search_input.send_keys(search_text)
        search_input.send_keys(Keys.ENTER)

        parent_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-175oi2r.r-1igl3o0.r-qklmqi.r-1adg3ll.r-1ny4l3l')))
        extracted_text_list = []
        for parent_div in parent_divs:
            nested_div = parent_div.find_element(By.CSS_SELECTOR, 'div.css-1rynq56.r-8akbws.r-krxsd3.r-dnmrzs.r-1udh08x.r-bcqeeo.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-bnwqim')
            text = nested_div.text
            extracted_text_list.append(text)
        return '\n\n'.join(extracted_text_list)
    try:
        driver.maximize_window()
        driver.get("https://twitter.com/login")
        time.sleep(5)

        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        email_input.send_keys(TWITTER_USER_NAME)

        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button.click()

        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(TWITTER_PASSWORD)

        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]')))
        button.click()

        search_text = "#generalavailability"
        extracted_text = extract_tweets(driver, search_text)
        producer.send('twitter-llm', value=extracted_text)
    except Exception as e:
        pass
        print(f"Error in scrape_twitter: {e}")
    finally:
        driver.quit()
def scrape_slashdot(driver):
    driver.get("https://slashdot.org/")
    time.sleep(5)
    all_element = driver.find_element(By.LINK_TEXT, "Software")
    all_element.click()

    def scroll_and_scrape_slashdot():
        # This function scrolls and scrapes data from Slashdot
        try:
            products = driver.find_elements(By.CSS_SELECTOR, "div.result-heading-texts")
            for product in products:
                product_name = product.find_element(By.CSS_SELECTOR, "h3").text
                description = product.find_element(By.CSS_SELECTOR, "div.description").text
                print(f"Product Name: {product_name}, Description: {description}")
        except Exception as e:
            print(f"Error extracting product details: {e}")

    while True:
        scroll_and_scrape_slashdot()
        time.sleep(5) 
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            next_button.click()
        except:
            print("No more pages to scrape for Slashdot.")
            break

def scrape_producthunt(driver):
    driver.get("https://www.producthunt.com/")
    time.sleep(5)
    all_element = driver.find_element(By.LINK_TEXT, "All")
    all_element.click()

    def scroll_and_scrape_producthunt():
        # This function scrolls and scrapes data from Product Hunt
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            containers = driver.find_elements(By.CSS_SELECTOR, "div.styles_titleItem__bCaNQ")
            for container in containers:
                product_name = container.find_element(By.TAG_NAME, "strong").text
                full_text = container.find_element(By.CSS_SELECTOR, "div.styles_titleTaglineItem__d5Rut").text
                parts = full_text.split("—")
                product_description = parts[1].strip() if len(parts) > 1 else "No description"
                topics = [topic.text for topic in container.find_elements(By.CSS_SELECTOR, "div.styles_underlinedLink__MUPq8, a.styles_underlinedLink__MUPq8")]
                print(f"Product Name: {product_name}, Description: {product_description}, Topics: {topics}")

    scroll_and_scrape_producthunt()
def setup_kafka_producer():
    producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda x: x.encode('utf-8'))
    return producer
def main():
        producer = setup_kafka_producer()
 
        # scrape_slashdot(driver)
        scrape_twitter(producer)
        # scrape_producthunt(driver)

      

if __name__ == "__main__":
    main()

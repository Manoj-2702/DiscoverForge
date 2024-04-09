from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from kafka import KafkaProducer
import time
import json

def setup_webdriver():
    service = Service("edgedriver_win64/msedgedriver.exe")
    return webdriver.Edge(service=service)

def setup_kafka_producer():
    print("Setting up Kafka producer")
    return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def scrape_slashdot(driver, producer):
    driver.get("https://slashdot.org/")
    time.sleep(5)
    all_element = driver.find_element(By.LINK_TEXT, "Software")
    all_element.click()

    def scroll_and_scrape_slashdot():
        try:
            products = driver.find_elements(By.CSS_SELECTOR, "div.result-heading-texts")
            for product in products:
                product_name = product.find_element(By.CSS_SELECTOR, "h3").text
                description = product.find_element(By.CSS_SELECTOR, "div.description").text
                data = {"name": product_name, "description": description}
                producer.send('Software', value=data)
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

def scrape_producthunt(driver, producer):
    driver.get("https://www.producthunt.com/")
    time.sleep(5)
    all_element = driver.find_element(By.LINK_TEXT, "All")
    all_element.click()

    def scroll_and_scrape_producthunt():
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
                data = {"name": product_name, "description": product_description, "topics": topics}
                producer.send('ProductHunt', value=data)

    scroll_and_scrape_producthunt()

def main():
    driver = setup_webdriver()
    producer = setup_kafka_producer()
    try:
        scrape_slashdot(driver, producer)
        scrape_producthunt(driver, producer)
        
    finally:
        driver.quit()
        producer.close()

if __name__ == "__main__":
    main()

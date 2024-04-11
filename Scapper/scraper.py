from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from kafka import KafkaProducer
import time
import json
from threading import Thread

def setup_webdriver():
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')
    service = Service("edgedriver_win64/msedgedriver.exe")
    return webdriver.Edge(service=service, options=options)

def setup_kafka_producer():
    print("Setting up Kafka producer")
    return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def scrape_slashdot(driver, producer):
    try:
        driver.maximize_window()
        driver.get("https://slashdot.org/")
        time.sleep(5)
        all_element = driver.find_element(By.LINK_TEXT, "Software")
        all_element.click()

        while True:
            products = driver.find_elements(By.CSS_SELECTOR, "div.result-heading-texts")
            for product in products:
                product_name = product.find_element(By.CSS_SELECTOR, "h3").text
                description = product.find_element(By.CSS_SELECTOR, "div.description").text
                data = {"name": product_name, "description": description}
                # Send data to Kafka
                producer.send('Software', value=data)

            time.sleep(5)
            try:
                next_button = driver.find_element(By.LINK_TEXT, "Next")
                next_button.click()
            except:
                print("No more pages to scrape for Slashdot.")
                break
    except Exception as e:
        print(f"Error in scrape_slashdot: {e}")
    finally:
        driver.quit()

def scrape_producthunt(driver, producer):
    try:
        driver.maximize_window()
        driver.get("https://www.producthunt.com/")
        time.sleep(5)
        all_element = driver.find_element(By.LINK_TEXT, "All")
        all_element.click()

        while True:
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
                # Send data to Kafka
                producer.send('ProductHunt', value=data)
            break
    except Exception as e:
        print(f"Error in scrape_producthunt: {e}")
    finally:
        driver.quit()

def scrape_sideprojectors(driver,producer):
    try:
        driver.maximize_window()
        driver.get("https://www.sideprojectors.com/#/")
        time.sleep(5)
        ids = ["input-project-type-blog", "input-project-type-domain", "input-project-type-other"]

        for id_value in ids:
            try:
                element = driver.find_element(By.ID, id_value)
                element.click()
            except:
                continue

        search_button=driver.find_element(By.XPATH, '//button[text()="Search"]')
        search_button.click()

        time.sleep(3)

        while True:
            last_height = driver.execute_script("return document.body.scrollHeight")
            products = driver.find_elements(By.CSS_SELECTOR, "a.project-item")
            for product in products:
                product_name = product.find_element(By.CSS_SELECTOR, ".name").text
                description = product.find_element(By.CSS_SELECTOR, "div.description").text
                date_span = product.find_elements(By.CSS_SELECTOR, "div.mt-6.flex.items-center span.gray-text")[-1].text
                product_doc = {"name": product_name, "description": description,"date": date_span}
                producer.send('SideProjectors', value=product_doc)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            try:
                next_button = driver.find_element(By.XPATH, '//button[text()="Next"]')
                next_button.click()
            except:
                print("No more pages to scrape for SideProjectors.")
                break

    except Exception as e:
        print(f"Error in scrape_slashdot: {e}")
    finally:
        driver.quit()


def main():
    producer = setup_kafka_producer()
    # Creating separate WebDriver instances for each thread
    driver1 = setup_webdriver()
    driver2 = setup_webdriver()
    driver3 = setup_webdriver()
    
    # Initialize and start threads
    thread1 = Thread(target=scrape_slashdot, args=(driver1, producer))
    thread2 = Thread(target=scrape_producthunt, args=(driver2, producer))
    thread3 = Thread(target=scrape_sideprojectors, args=(driver3, producer))
    
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()
    thread3.join()

    producer.close()

if __name__ == "__main__":
    main()

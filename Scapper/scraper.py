from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from kafka import KafkaProducer
import time
import json
from threading import Thread
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
load_dotenv()
TWITTER_USER_NAME=os.getenv("TWITTER_USER_NAME")
TWITTER_PASSWORD=os.getenv("TWITTER_PASSWORD")
def setup_webdriver():
    chrome_options = Options()   
    chrome_options.add_argument("--disable-popup-blocking")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service,)
 

def setup_kafka_producer():
    print("Setting up Kafka producer")
    return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def scrape_slashdot(producer):
    try:
        driver = setup_webdriver()
        # driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        driver.get("https://slashdot.org/")
        # time.sleep(5)
        all_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Software")))
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
                # driver.quit()
                break
            # finally:
            #   driver.quit()
    except NoSuchElementException as e:
       
        print(f"Element not found: {e}")
    except ElementNotInteractableException as e:
     
        print(f"Element not interactable: {e}")
    except TimeoutException as e:
       
        print(f"Operation timed out: {e}")
    except Exception as e:
        
        print(f"Error in scrape_slashdot: {e}")


def scrape_producthunt(producer):
    try:
        
        driver = setup_webdriver()
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.producthunt.com/")
        # time.sleep(5)
        all_element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "All")))
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
                producer.send('Software', value=data)
                
            break
       
    except Exception as e:  
        print(f"Error in scrape_producthunt: {e}")

def scrape_sideprojectors(producer):
    try:
        driver = setup_webdriver()
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.sideprojectors.com/#/")
        # time.sleep(5)
        ids = ["input-project-type-blog", "input-project-type-domain", "input-project-type-other"]

        for id_value in ids:
            try:
                # element = wait.until(EC.element_to_be_clickable((By.ID, id_value)))
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
                producer.send('Software', value=product_doc)

            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            try:
                next_button = driver.find_element(By.XPATH, '//button[text()="Next"]')
                next_button.click()
            except:
                print("No more pages to scrape for SideProjectors.")
                break
        # driver.quit()

    except Exception as e:
        print(f"Error in scrape_slashdot: {e}")

def scrape_twitter(driver, producer):
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
        print(f"Error in scrape_twitter: {e}")
    finally:
        driver.quit()

def main():
    producer = setup_kafka_producer()
    # Initialize and start threads
    thread1 = Thread(target=scrape_slashdot, args=(producer,))
    thread2 = Thread(target=scrape_producthunt, args=(producer,))
    thread3 = Thread(target=scrape_sideprojectors, args=(producer,))
    thread4 = Thread(target=scrape_twitter, args=(producer,))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    producer.close()

if __name__ == "__main__":
    main()

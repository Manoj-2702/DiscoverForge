from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.keys import Keys
import os, time, json, requests
from kafka import KafkaProducer
from threading import Thread
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service

load_dotenv()
TWITTER_USER_NAME=os.getenv("TWITTER_USER_NAME")
TWITTER_PASSWORD=os.getenv("TWITTER_PASSWORD")

def setup_webdriver():
    chrome_options = Options()   
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080") # Adjust as needed
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Specify the path to Chrome in Docker

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# def setup_webdriver():
#     chrome_options = Options()   
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     # Directly reference the ChromeDriver path
#     service = ChromeService(executable_path="/usr/local/bin/chromedriver")
#     return webdriver.Chrome(service=service, options=chrome_options)

 

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
                try:
                    product_name = container.find_element(By.TAG_NAME, "strong").text
                    full_text = container.find_element(By.CSS_SELECTOR, "div.styles_titleTaglineItem__d5Rut").text
                    parts = full_text.split("—")
                    product_description = parts[1].strip() if len(parts) > 1 else "No description"
                    topics = [topic.text for topic in container.find_elements(By.CSS_SELECTOR, "div.styles_underlinedLink__MUPq8, a.styles_underlinedLink__MUPq8")]
                    data = {"name": product_name, "description": product_description, "topics": topics}
                    producer.send('Software', value=data)   
                except Exception as e:
                    print(f"Error in scrape_producthunt: {e}")
                    continue
    except Exception as e: 
        pass
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
        pass
        print(f"Error in scrape_slashdot: {e}")

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
        producer.send('x-llm', value=extracted_text)
    except Exception as e:
        pass
        print(f"Error in scrape_twitter: {e}")
    finally:
        driver.quit()

def betalist_scraper(producer):
    topics_data = []
    
    def scrape_and_print_all_details(base_url, href_list, producer):
        for href in href_list:
            full_url = urljoin(base_url, href)
            attempt_count = 0
            while attempt_count < 3:  # Retry up to 3 times
                try:
                    # Send a GET request to the full URL
                    response = requests.get(full_url)
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    break
                except requests.RequestException as e:
                    attempt_count += 1
                    print(f"Failed to fetch {full_url}, attempt {attempt_count}. Error: {e}")
                    time.sleep(2)  # Wait 2 seconds before retrying
            if attempt_count == 3:
                print(f"Failed to process {full_url} after multiple attempts.")
                continue  # Skip this URL

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            details_divs = soup.find_all('div', class_='startupCard__details')
            startups = []
            for div in details_divs:
                name_tag = div.find('a', class_='block whitespace-nowrap text-ellipsis overflow-hidden font-medium')
                name = name_tag.text.strip() if name_tag else "Name not found"
                href = name_tag.get('href') if name_tag else "Href not found"
                description_div = div.find('a', class_='block text-gray-500 dark:text-gray-400')
                description = description_div.get_text(strip=True) if description_div else "Description not found"
                
                startups.append({"name": name, "href": href})
                message = {'name': name, 'description': description, 'href': href}
                
                producer.send('Software', message)
                producer.flush()

            topics_data.append({"link_topic": full_url, "startups": startups})
        
        # Writing data to JSON file
        try:
            with open('output_sites2.json', 'w') as f:
                json.dump(topics_data, f, indent=4)
        except IOError as e:
            print(f"Error writing to file: {e}")

    url = "https://betalist.com/topics"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.find_all('div', class_='myContainer')
        if len(containers) >= 2:
            container = containers[1]
            links = container.find_all('a', class_='flex items-center gap-1 px-2 hover:bg-gray-100 group gap-4 hover:-my-[1px]')
            href_list = [link.get('href') for link in links]
            scrape_and_print_all_details("https://betalist.com", href_list, producer)
        else:
            print("There are less than two 'myContainer' divs on the page.")
    except requests.RequestException as e:
        print(f"Failed to load page {url}: {e}")

def main():
    producer = setup_kafka_producer()
    # Initialize and start threads
    thread1 = Thread(target=scrape_slashdot, args=(producer,)) 
    thread2 = Thread(target=scrape_producthunt, args=(producer,))   #no crowler required
    thread3 = Thread(target=scrape_sideprojectors, args=(producer,))
    thread4 = Thread(target=scrape_twitter, args=(producer,))
    thread5 = Thread(target=betalist_scraper, args=(producer,))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

    producer.close()

if __name__ == "__main__":
    main()

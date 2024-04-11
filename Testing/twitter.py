# from selenium import webdriver
# from selenium.webdriver.edge.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# import time
# import pymongo

# def setup_webdriver():
#     options = webdriver.EdgeOptions()
#     options.add_argument('--headless')
#     service = Service("edgedriver_win64/msedgedriver.exe")
#     return webdriver.Edge(service=service, options=options)

# def write_to_file(filename, content):
#     with open(filename, "w") as file:
#         file.write(content)
#     print(f"Data has been written to {filename} file.")


# def extract_tweets(driver, search_text):
#     search_input = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='SearchBox_Search_Input']")))
#     search_input.send_keys(search_text)
#     search_input.send_keys(Keys.ENTER)

#     parent_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-175oi2r.r-1igl3o0.r-qklmqi.r-1adg3ll.r-1ny4l3l')))
#     extracted_text_list = []
#     for parent_div in parent_divs:
#         nested_div = parent_div.find_element(By.CLASS_NAME, 'css-175oi2r')
#         text = nested_div.text
#         extracted_text_list.append(text)
#     return '\n\n'.join(extracted_text_list)

# def main():
#     driver = setup_webdriver()
#     driver.get("https://twitter.com/login")
#     email_input = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.NAME, "text"))
#     )
#     email_input.send_keys("@270203manoj")

#     next_button = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
# )
#     next_button.click()

#     password_input = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.NAME, "password"))
#     )

#     password="Manu@86185"

#     # Input the password
#     password_input.send_keys(password)


#     button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
#     )

#     # Click the button
#     button.click()

#     search_text = "#hydraforbengaluru"
#     extracted_text = extract_tweets(driver, search_text)
#     write_to_file("extracted_text.txt", extracted_text)

#     driver.quit()

# if __name__ == "__main__":
#     main()


from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymongo

CONNECTION_STRING = "mongodb://localhost:27017/"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client["Products"]
collection = db["product_info4"]

service = Service("edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service)
driver.maximize_window()

driver.get("https://twitter.com/login")
time.sleep(5)

email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
email_input.send_keys("@270203manoj")

next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
)
next_button.click()

password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

password_input.send_keys("Manu@86185")

button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
    )

    # Click the button
button.click()

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

def write_to_file(filename, content):
    with open(filename, "w") as file:
        file.write(content+"\n\n\n")
    print(f"Data has been written to {filename} file.")


search_text = "#generalavailability"
extracted_text = extract_tweets(driver, search_text)
write_to_file("extracted_text.txt", extracted_text)
print(extracted_text)


time.sleep(10)


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
        email_input.send_keys("@270203manoj")

        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
        next_button.click()

        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys("Manu@86185")

        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]')))
        button.click()

        search_text = "#hydraforbengaluru"
        extracted_text = extract_tweets(driver, search_text)
        producer.send('tw', value=extracted_text)
    except Exception as e:
        print(f"Error in scrape_twitter: {e}")
    finally:
        driver.quit()
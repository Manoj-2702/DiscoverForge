from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_webdriver():
    chrome_options = Options()
    # Add any options you need
    chrome_options.add_argument("--headless")

    # Ensure you are using the Service object correctly with webdriver_manager
    service = Service(ChromeDriverManager().install())

    # Pass options using the options parameter
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

driver = setup_webdriver()

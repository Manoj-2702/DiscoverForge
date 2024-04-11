import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from kafka import KafkaProducer
import json

def setup_kafka_producer():
    # Initialize Kafka producer with bootstrap servers
    return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def betalist_scraper(producer):

    def scrape_and_print_all_details(base_url, href_list,producer):
        for href in href_list:
            # Construct the full URL
            full_url = urljoin(base_url, href)

            # Send a GET request to the full URL
            response = requests.get(full_url)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <div> tags with class 'startupCard__details'
            details_divs = soup.find_all('div', class_='startupCard__details')

            # Extract and print the name and description from each <div>
            for div in details_divs:
                # Find the <a> tag for name
                name_tag = div.find('a', class_='block whitespace-nowrap text-ellipsis overflow-hidden font-medium')
                name = name_tag.text.strip() if name_tag else "Name not found"

                # Find the <div> tag for description
                description_div = div.find('a', class_='block text-gray-500 dark:text-gray-400')
                description = description_div.get_text(strip=True) if description_div else "Description not found"

                message = {'name': name, 'description': description}

                # Send the message to the Kafka topic
                producer.send('Software', message)
                producer.flush()



    # URL of the page to scrape
    url = "https://betalist.com/topics"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <div> tags with class 'myContainer'
    containers = soup.find_all('div', class_='myContainer')

    # Ensure there are at least two containers
    if len(containers) >= 2:
        # Select the second container
        container = containers[1]

        # Find all <a> tags within the selected container with the specified class
        links = container.find_all('a', class_='flex items-center gap-1 px-2 hover:bg-gray-100 group gap-4 hover:-my-[1px]')

        # Extract and store the href attributes in a list
        href_list = [link.get('href') for link in links]

        # Scrape and print all links from each website
        base_url = "https://betalist.com"
        scrape_and_print_all_details(base_url, href_list,producer)
    else:
        print("There are less than two 'myContainer' divs on the page.")




def main():
    producer = setup_kafka_producer()

    betalist_scraper(producer)

    producer.close()



if __name__ == "__main__":
    main()
import requests
from bs4 import BeautifulSoup
import json
import threading
from kafka import KafkaProducer

def setup_kafka_producer():
    # Initialize Kafka producer with bootstrap servers
    return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def crawl_betalist(startups_and_links_file,producer):

    def extract_urls_from_json(filename, start_idx, end_idx):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine the elements to read
        data_chunk = data[start_idx:end_idx]
        
        # Iterate through the data chunk and extract URLs
        urls = []
        for entry in data_chunk:
            if "link_topic" in entry:
                urls.append(entry["link_topic"])
        
        return urls

    def scrape_category_details(url):
        response = requests.get(url)
        details = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            container = soup.find('div', class_='infinite-startups')
            if container:
                links = container.find_all('a', class_="block whitespace-nowrap text-ellipsis overflow-hidden font-medium")
                for link in links:
                    # For each link, store both its text and the href attribute
                    details.append({
                        "text": link.get_text(strip=True),
                        "href": link.get('href')  # Extract the href attribute
                    })
        else:
            print(f"Failed to fetch the page for {url}, status code: {response.status_code}")
        return details

    def scrape_details_from_urls(urls):
        startup_details = []

        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('h2').get_text(strip=True) if soup.find('h2') else 'Title Not Found'
                main_content_div = soup.find('div', class_='main content')
                description = ' '.join(p.get_text(strip=True) for p in main_content_div.find_all('p')) if main_content_div else 'Description Not Found'
                startup_details.append({"title": title, "description": description})
            else:
                print(f"Failed to fetch the page for URL: {url}, status code: {response.status_code}")
                startup_details.append({"title": 'Title Not Found', "description": 'Description Not Found'})
        return startup_details

    def check_for_new_products(url, filename=startups_and_links_file):
        category_details = scrape_category_details(url)
        
        # Load existing data from the JSON file
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_hrefs = set()
        for entry in existing_data:
            if entry["link_topic"] == url and entry["startups"]:
                for startup in entry["startups"]:
                    existing_hrefs.add(startup["href"])

        new_products_found = False
        
        # Check if any new products are found
        new_product_hrefs = []
        for detail in category_details:
            if detail["href"] not in existing_hrefs:
                new_products_found = True
                new_product_hrefs.append(detail)

        # Print new product names and scrape details
        if new_product_hrefs:
            
            for detail in new_product_hrefs:
                print(f"New product found: {detail['text']}")
                base_url = "https://betalist.com"
                href = detail['href']
                full_url = f"{base_url}{href}"
                startup_details = scrape_details_from_urls([full_url])
                for startup in startup_details:
                    print(f"text: {detail['text']}")
                    print(f"Title: {startup['title']}")
                    print(f"Description: {startup['description']}")
                    data = {
                        "text": detail['text'],
                        "title": startup['title'],
                        "description": startup['description']
                    }
                    producer.send('Software', value=data)
                    print("Data sent to Kafka topic 'Software'") #### send details of new product through kafka
        
        # Append new products to the JSON file
        if new_product_hrefs:
            for detail in new_product_hrefs:
                entry = {
                    "text": detail["text"],
                    "href": detail["href"]
                }
                for existing_entry in existing_data:
                    if existing_entry["link_topic"] == url:
                        existing_entry["startups"].append(entry)
                        break
                else:
                    existing_data.append({"link_topic": url, "startups": [entry]})
            
            # Write the updated data back to the JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)

        return new_products_found

    def run_crawler(start_idx, end_idx,producer):
        filename = startups_and_links_file
        urls = extract_urls_from_json(filename, start_idx, end_idx)
        for url in urls:
            new_products = check_for_new_products(url,producer)

            if not new_products:
                print("No new products found.")

    # JSON filename
    filename = startups_and_links_file

    # Calculate the number of elements
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    num_elements = len(data)

    # Divide the elements into two parts
    mid_idx = num_elements // 2

    # Create two threads to run the crawlers simultaneously
    thread1 = threading.Thread(target=run_crawler, args=(0, mid_idx,producer))
    thread2 = threading.Thread(target=run_crawler, args=(mid_idx, num_elements,producer))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for the threads to finish
    thread1.join()
    thread2.join()




def main():
    producer = setup_kafka_producer()




    crawl_betalist('output_sites2.json',producer)




    producer.close()



if __name__ == "__main__":
    main()

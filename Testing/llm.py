import json
from dotenv import load_dotenv
from os import getenv
import google.generativeai as genai
import requests
from pymongo import MongoClient
from datetime import datetime

load_dotenv()
api_token = getenv("G2_API_KEY")
mongo_conn_string = getenv("MONGO_CONN_STRING")
google_token=getenv("GOOGLE_API_KEY")

client = MongoClient(mongo_conn_string)
db = client.g2hack
unavailable_products_collection = db.unavailableProducts

def list_products_google(msgData):
    genai.configure(api_key = google_token)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"""{msgData} \n Imagine a digital assistant meticulously analyzing a diverse collection of announcements related to the launch of new products and services in various industries. This assistant is tasked with identifying and categorizing each product or service mentioned, discerning whether each one represents a fresh market entry or an update to an existing offering. The goal is to compile this information into a straightforward, accessible format. Specifically, the assistant is required to present its findings as a list, focusing solely on the names of these products or services, neatly organized into an array. The array should exclusively contain the names, clearly distinguishing between novel introductions and updates to pre-existing entities, thus providing a clear, concise overview of the recent developments highlighted in the announcements. The naming should be in this format. Status and Product_Name. Give the output in a json format which gives the product name and the status of the same whether its a new product or just a update to the existing product. The status should either be New Product or Update to existing product. """)

    return response.text

msg=""" 
ANNOUNCEMENT !
@CrossTheAges just released the #GeneralAvailability of the #TCG game and with it we are proud to be launching our official website to help new players and keep you updated! 

https://arkhante.com

Let s go through what you will find there 

No-code editor updates are now generally available for Stream Analytics! Simplify your data analytics and processing tasks without writing any code. Learn more about these updates and try them out today.

#NoCode #DataAnalytics #GeneralAvailability
https://bit.ly/3lpDzs1

Revolutionizing Real-Time Multiplayer Collaboration with AI: Sequoia Capital Backs PartyKit

#AI #artificialintelligence #flexibility #generalavailability #HumanAIcollaboration #llm #machinelearning #Media #opensourcedeploymentplatform #PartyKit

https://multiplatform.ai/revolutionizing-real-time-multiplayer-collaboration-with-ai-sequoia-capital-backs-partykit/ 

Improved Text Analytics In BigQuery: #Search Features Now GA https://cyberpogo.com/2022/11/25/improved-text-analytics-in-bigquery-search-features-now-ga/  #googlecloud #generalavailability #bigquery #indexing #query #dataanalytics

Improved Text Analytics In BigQuery: #Search Features Now GA https://globalcloudplatforms.com/2022/11/25/improved-text-analytics-in-bigquery-search-features-now-ga/  #indexing #query #generalavailability #bigquery #dataanalytics #googlecloud
"""
def list_products(api_token, filter_name=None):
    url = "https://data.g2.com/api/v1/products"
    headers = {
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/vnd.api+json"
    }
    params = {'filter[name]': filter_name} if filter_name else {}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch products, status code: {response.status_code}")
        return None
    

def process_message(message_data):
    x=list_products_google(message_data)
    try:
        # Try to load it as JSON if it's a string (assuming json_response might be a string)
        products = json.loads(x)
    except json.JSONDecodeError:
        # If json_response is already a dictionary
        products = x
    for product in products:
        product_name=None
        if isinstance(product, dict):
            if product.get("Status") == "New Product":  # Assuming the correct status is "new product"
                product_name = product.get('Product Name')
        if product_name:
            g2_response = list_products(api_token, filter_name=product_name)
            if g2_response and not g2_response.get('data'):
                print(f"Product not found in G2: {product_name}")
                document = {
                    "product_name": product_name,
                    "timestamp": datetime.now()
                }
                unavailable_products_collection.insert_one(document)
            else:
                print(f"Product found in G2: {product_name}")


process_message(msg)
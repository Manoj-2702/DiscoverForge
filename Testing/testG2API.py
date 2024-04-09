# LIST ALL THE PRODUCTS
import requests
import json
from dotenv import load_dotenv
from os import getenv
load_dotenv()
api_token = getenv("G2_API_KEY")


def list_products(api_token, filter_name='None', filter_domain=None, filter_slug=None):
    url = "https://data.g2.com/api/v1/products"
    headers = {
        "Authorization": f"Token token={str(api_token)}",
        "Content-Type": "application/vnd.api+json"
    }
    params = {}
    if filter_name:
        params['filter[name]'] = filter_name
    if filter_domain:
        params['filter[domain]'] = filter_domain
    if filter_slug:
        params['filter[slug]'] = filter_slug

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to fetch products, status code: {response.status_code}"

# Example usage

# Adjust the filter arguments as needed
print(list_products(api_token, filter_name="StealthGPT"))
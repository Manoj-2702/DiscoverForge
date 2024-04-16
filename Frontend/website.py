import streamlit as st
import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
load_dotenv()
mongo_url=os.getenv("MONGO_CONN_STRING")

client = MongoClient("mongodb+srv://g2hack:g2hack%40123@g2.0fzaw48.mongodb.net/?retryWrites=true&w=majority")
db = client['g2hack']  
collection = db['unavailableProducts']


def main():
    st.title("Try Catch Devs")
    st.text("Developed by- Manoj Kumar HS, Nandish NS, Abhiram Karanth")
    input_date = st.date_input("Select date", value=datetime.date.today())
    st.write(f"Selected date: {input_date}")
    st.write(" ")

    start_of_day = datetime.datetime(input_date.year, input_date.month, input_date.day)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    query = {
        "timestamp": {
            "$gte": start_of_day,
            "$lt": end_of_day
        }
    }
    results = collection.find(query).sort("product_name", -1)
    unique_products = {}
    for result in results:
        product_name = result["product_name"]
        if product_name not in unique_products:
            unique_products[product_name] = result.get("desc", "No description available")

    # Prepare data for display
    products = [{"Product Name": name, "Description": desc} for name, desc in unique_products.items()]
    
    # products = [{"Product Name": result["product_name"], "Description": result.get("desc", "No description available")}
    #             for result in results]

    count = len(products)
    st.write(f"Number of unique products on the selected date: {count}")

    if products:
        df = pd.DataFrame(products)
        st.table(df)
    else:
        st.write("No products found for the selected date.")


if __name__ == "__main__":
    main()

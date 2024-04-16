import Flask
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import datetime

load_dotenv()
mongo_url=os.getenv("MONGO_CONN_STRING")
client = MongoClient("mongodb+srv://g2hack:g2hack%40123@g2.0fzaw48.mongodb.net/?retryWrites=true&w=majority")
db = client['g2hack']  
collection = db['unavailableProducts']


app = Flask(__name__)


@app.route('/getdata', methods=['GET'])
def getdata():
    start_of_day = datetime.datetime(input_date.year, input_date.month, input_date.day)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    query = {
        "timestamp": {
            "$gte": start_of_day,
            "$lt": end_of_day
        }
    }
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$product_name",
            "description":  "$desc"
        }},
        {"$sort": {"_id": 1}}  # Sort by product name
    ]
    results = collection.aggregate(pipeline)
    products = [{"Product Name": result["_id"], "Description": result.get("desc", "No description available")}
                for result in results]

    count = len(products)

    if products:
        df = pd.DataFrame(products)
        return df
    else:
        print("No products found for the selected date.")

    return "Data Received Successfully"



@app.route('/')
def serverStatus():
    return "✨Server is Up and Running✨"


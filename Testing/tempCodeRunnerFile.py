CONNECTION_STRING = "mongodb://localhost:27017/"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client["Products"]
collection = db["product_info3"]

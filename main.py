from crawler import Crawler
import json
from pymongo import MongoClient
import os

# Delete output.json if it exists
if os.path.exists("output.json"):
    os.remove("output.json")

# Scrape the website
url = 'https://edition.cnn.com/'
scraper = Crawler(url, max_scrolls=50, pause_time=2, max_links=2, output_file="output.json")
scraper.run()

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "Crawler"
COLLECTION_NAME = "news"
JSON_FILE_PATH = "output.json"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Load data from JSON file
with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Insert data into MongoDB
if isinstance(data, list):
    collection.insert_many(data)
else:
    collection.insert_one(data)

print(f"Data successfully inserted into {DATABASE_NAME}.{COLLECTION_NAME}")

# Remove duplicates
pipeline = [
    {
        "$group": {
            "_id": {
                "url": "$url",
                # Add more fields if needed to identify duplicates
            },
            "count": {"$sum": 1},
            "docs": {"$push": "$_id"}
        }
    },
    {
        "$match": {
            "count": {"$gt": 1}
        }
    }
]

# Execute the aggregation pipeline to find duplicates
results = collection.aggregate(pipeline)

# Process results to remove duplicates
for result in results:
    # Keep the first document and delete the rest
    docs_to_keep = [result['docs'][0]]
    docs_to_delete = result['docs'][1:]

    # Delete duplicate documents
    collection.delete_many({
        "_id": {"$in": docs_to_delete}
    })

print("Duplicate documents have been removed.")

# Close the connection
client.close()

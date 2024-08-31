from crawler import Crawler
import json
from pymongo import MongoClient
import os

if os.path.exists("output.json"):
        os.remove("output.json")

# Replace with the target URL
url = 'https://farsnews.ir/showcase'

# Create an instance of WebScraper
scraper = Crawler(url, max_scrolls=50, pause_time=2, max_links=5, output_file="output.json")

# Run the scraper
scraper.run()

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "SCRAPER"
COLLECTION_NAME = "news"
JSON_FILE_PATH = "output.json"

# Establish a connection to MongoDB
client = MongoClient(MONGO_URI)

# Access the database
db = client[DATABASE_NAME]

# Access the collection
collection = db[COLLECTION_NAME]

# Read the JSON file with UTF-8 encoding
with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Assign a custom _id to each document
if isinstance(data, list):
    collection.insert_many(data)
else:
    collection.insert_one(data)

# Print success message
print(f"Data successfully inserted into {DATABASE_NAME}.{COLLECTION_NAME}")

client.close()
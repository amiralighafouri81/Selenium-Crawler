from crawler import Crawler
from pymongo import MongoClient
import json
import os

# Delete output.json if it exists
if os.path.exists("output.json"):
    os.remove("output.json")

# Scrape the website
urls = []
with open('urls.txt', 'r') as file:
    for line in file:
        line = line.strip()
        url = f"{line}"
        urls.append(url)

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "Crawler"
COLLECTION_NAME = "news"
JSON_FILE_PATH = "output.json"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

for url in urls:
    scraper = Crawler(url, max_scrolls=50, pause_time=2, max_links=9, output_file="output.json")
    scraper.run()

    # Load data from JSON file
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Insert data into MongoDB only if it is a non-empty list or dict
    if data and isinstance(data, list):
        collection.insert_many(data)
        print(f"Inserted {len(data)} documents into {DATABASE_NAME}.{COLLECTION_NAME}")
    elif isinstance(data, dict):
        collection.insert_one(data)
        print(f"Inserted 1 document into {DATABASE_NAME}.{COLLECTION_NAME}")
    else:
        print(f"No data to insert for {url}")

# Close the connection
client.close()

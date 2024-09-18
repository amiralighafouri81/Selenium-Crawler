from crawler import Crawler
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

def run_crawler(url):
    scraper = Crawler(url, db_collection=collection, max_scrolls=50, pause_time=5, max_links=5)
    scraper.run()

urls = []
with open('urls.txt', 'r') as file:
    for line in file:
        line = line.strip()
        urls.append(line)

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "Crawler-news"
COLLECTION_NAME = "news"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(run_crawler, urls)

client.close()


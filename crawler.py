from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time
import json


class Crawler:
    def __init__(self, url, max_scrolls=50, pause_time=2, max_links=5, output_file="output.json"):
        self.url = url
        self.max_scrolls = max_scrolls
        self.pause_time = pause_time
        self.max_links = max_links
        self.output_file = output_file

        # Set up Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_experimental_option("detach", True)  # Keep the browser open after the script finishes

        # Initialize the WebDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def get_domain(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def is_same_domain(self, main_url, new_url):
        main_domain = self.get_domain(main_url)
        new_domain = self.get_domain(new_url)

        if 'ads' in new_url or 'redirect' in new_url:
            return False

        return main_domain in new_domain

    def scroll_incrementally_and_collect_links(self):
        all_links = set()  # Use a set to avoid duplicates
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        main_domain = self.get_domain(self.url)

        for _ in range(self.max_scrolls):
            # Scroll down by a small increment (to trigger lazy loading)
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(self.pause_time)  # Wait for content to load

            anchor_elements = self.driver.find_elements(By.TAG_NAME, "a")
            for element in anchor_elements:
                href = element.get_attribute("href")
                if href and self.is_same_domain(self.url, href):  # Check if link belongs to the same domain
                    all_links.add(href)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return all_links

    def crawl_and_extract_data(self, links):
        all_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "div", "img", "form", "input", "textarea"]
        all_attributes = ["src", "href", "alt", "title", "value"]

        data = []

        for link in list(links)[:self.max_links]:
            page_data = {"url": link}
            page_data.update({tag: [] for tag in all_tags})

            print(f"Processing {link}...")
            try:
                self.driver.get(link)
                time.sleep(2)

                for tag in all_tags:
                    elements = self.driver.find_elements(By.TAG_NAME, tag)
                    for element in elements:
                        text = element.text.strip()
                        if text:
                            page_data[tag].append({"type": "text", "value": text})

                for tag in all_tags:
                    elements = self.driver.find_elements(By.TAG_NAME, tag)
                    for element in elements:
                        for attr in all_attributes:
                            value = element.get_attribute(attr)
                            if value:
                                page_data[tag].append({"type": "attribute", "attribute": attr, "value": value})

            except Exception as e:
                page_data["error"] = str(e)

            data.append(page_data)

        # Write the collected data to a JSON file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Data has been saved to {self.output_file}")

    def run(self):
        # Navigate to the webpage
        self.driver.get(self.url)

        # Scroll incrementally and collect all links
        all_links = self.scroll_incrementally_and_collect_links()

        # Crawl and extract data from the first 'max_links' collected links and store it in a JSON file
        self.crawl_and_extract_data(all_links)

        self.driver.quit()

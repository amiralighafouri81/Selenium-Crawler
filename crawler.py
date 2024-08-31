from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
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

    def scroll_incrementally_and_collect_links(self):
        all_links = set()  # Use a set to avoid duplicates
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(self.max_scrolls):
            # Scroll down by a small increment (to trigger lazy loading)
            self.driver.execute_script("window.scrollBy(0, 1000);")  # Adjust the increment value as needed
            time.sleep(self.pause_time)  # Wait for content to load

            # Re-evaluate the DOM for new anchor elements
            anchor_elements = self.driver.find_elements(By.TAG_NAME, "a")
            for element in anchor_elements:
                href = element.get_attribute("href")
                if href and len(href) > 0:  # Ensure href is not empty
                    all_links.add(href)

            # Check if the scroll height has changed (i.e., new content has loaded)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return all_links

    def crawl_and_extract_data(self, links):
        all_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "div", "img", "form", "input", "textarea"]
        all_attributes = ["src", "href", "alt", "title", "value"]

        data = []  # List to hold all the data
        seen_content = set()  # Set to track unique content

        # Process only the first 'max_links' links
        for link in list(links)[:self.max_links]:
            page_data = {"url": link, "content": []}  # Dictionary to store data for each page
            print("processing ...")
            try:
                self.driver.get(link)
                time.sleep(2)  # Adjust the wait time as needed

                # Extract text from tags
                for tag in all_tags:
                    elements = self.driver.find_elements(By.TAG_NAME, tag)
                    for element in elements:
                        text = element.text.strip()
                        if text:  # Only add non-empty text
                            content_tuple = (tag, "text", text)
                            if content_tuple not in seen_content:
                                seen_content.add(content_tuple)
                                page_data["content"].append({"tag": tag, "type": "text", "value": text})

                # Extract attributes from tags
                for tag in all_tags:
                    elements = self.driver.find_elements(By.TAG_NAME, tag)
                    for element in elements:
                        for attr in all_attributes:
                            value = element.get_attribute(attr)
                            if value:
                                content_tuple = (tag, "attribute", attr, value)
                                if content_tuple not in seen_content:
                                    seen_content.add(content_tuple)
                                    page_data["content"].append(
                                        {"tag": tag, "type": "attribute", "attribute": attr, "value": value})

            except Exception as e:
                page_data["error"] = str(e)  # Store any error messages

            data.append(page_data)  # Add the page data to the main list

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

        # Close the browser window (comment this out if you want to keep the browser open)
        self.driver.quit()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import math

# Path to ChromeDriver executable
CHROMEDRIVER_PATH = "C:/chromedriver-win64/chromedriver.exe"

# Target URL containing FAQ cards
URL = "https://www.askiitm.com/resources?tab=resources-quickreads"

# Max number of FAQs to extract
MAX_ITEMS = 30

# Output file for storing extracted data
OUTPUT_FILE = "faq_data.json"

# Configure headless browser settings
options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
service = Service(CHROMEDRIVER_PATH)

# Initialize Chrome WebDriver with above options
driver = webdriver.Chrome(service=service, options=options)

# Open the main FAQ listing page
driver.get(URL)

# Scroll to load more FAQ items dynamically
SCROLL_PAUSE_TIME = 2
MAX_SCROLLS = math.ceil(MAX_ITEMS / 10) + 5  # Estimate based on items per scroll

last_count = 0
for _ in range(MAX_SCROLLS):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    # Re-parse page source after scrolling
    soup = BeautifulSoup(driver.page_source, "html.parser")
    faq_items = soup.find_all("div", class_="w-dyn-item")

    # Stop scrolling if enough items loaded or no new items found
    if len(faq_items) >= MAX_ITEMS:
        break
    if len(faq_items) == last_count:
        break
    last_count = len(faq_items)

# Final parse after scrolling is done
soup = BeautifulSoup(driver.page_source, "html.parser")
faq_items = soup.find_all("div", class_="w-dyn-item")
print("FAQ cards found on page:", len(faq_items))

# List to store scraped data
data = []

# Loop through each FAQ card
for idx, item in enumerate(faq_items):
    if idx >= MAX_ITEMS:
        break
    try:
        # Extract the question text
        question_h3 = item.find(lambda tag: tag.name == "h3" and tag.get("class") and "articel-chip-title" in tag.get("class"))
        question = question_h3.get_text(strip=True) if question_h3 else ""
        if not question:
            print(f"[{idx}] No question found, skipping.")
            continue

        # Extract the category/tag of the FAQ
        tag_div = item.find("div", attrs={"fs-cmsfilter-field": "category"})
        tag = tag_div.get_text(strip=True) if tag_div else "Unknown"

        # Extract link to the detailed FAQ page
        a_tag = item.find("a", class_="link-block w-inline-block")
        link = ""
        if a_tag and a_tag.has_attr("href"):
            link = a_tag["href"]
            if link.startswith("/"):
                link = "https://www.askiitm.com" + link

        # Extract full answer and related questions from the detail page
        answer = ""
        suggested_questions = []
        if link:
            # Open link in a new browser tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            try:
                # Wait until the rich-text answer div is present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.rich-text-wrapper.w-richtext"))
                )
                detail_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract answer content
                answer_div = detail_soup.find("div", class_="rich-text-wrapper w-richtext")
                answer = answer_div.get_text(separator=" ", strip=True) if answer_div else "Unknown"

                # Extract suggested question blocks from bottom section
                suggestion_items = detail_soup.select("div.reads-collection-list-wrapper div.reads-collection-item")
                for s_item in suggestion_items:
                    s_h3 = s_item.find(lambda tag: tag.name == "h3" and tag.get("class") and "articel-chip-title" in tag.get("class"))
                    s_a = s_item.find("a", class_="link-block w-inline-block")
                    if s_h3 and s_a and s_a.has_attr("href"):
                        s_question = s_h3.get_text(strip=True)
                        s_href = s_a["href"]
                        if s_href.startswith("/"):
                            s_href = "https://www.askiitm.com" + s_href
                        suggested_questions.append({
                            "question": s_question,
                            "href": s_href
                        })
            except Exception as e:
                print(f"[{idx}] Error extracting answer or suggestions: {e}")
            # Close detail tab and return to main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Store structured FAQ entry
        data.append({
            "tag": tag,
            "question": question,
            "href": link,
            "answer": answer,
            "suggested_questions": suggested_questions
        })
    except Exception as e:
        print(f"Error while parsing item {idx}:", e)
        continue

# Close the browser after scraping
driver.quit()

# Save the extracted data to JSON file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Scraping done. Saved {len(data)} items to {OUTPUT_FILE}.")
print("Data sample:", data[:2])  # Print first two items as a sample
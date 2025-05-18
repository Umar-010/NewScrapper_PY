import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

CACHE_FILE = "cached_news.json"
EXPORT_DIR = "exports"
SOURCES_FILE = "news_sources.json"

def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["sources"]

def scrape_headlines(sources):
    headlines = []
    for source in sources:
        try:
            print(f"Scraping {source['name']}...")
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.select(source["headline_selector"])
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    headlines.append({"source": source["name"], "headline": text})
        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")
    return headlines

def cache_results(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cached():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def filter_headlines(headlines, keyword):
    result = []
    for h in headlines:
        if keyword.lower() in h["headline"].lower():
            result.append(h)
    return result

def display_table(headlines):
    print("\nFiltered Headlines:\n")
    print("-" * 80)
    for h in headlines:
        print(f"[{h['source']}] {h['headline']}")
    print("-" * 80)

def export_to_csv(headlines):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"news_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "headline"])
        writer.writeheader()
        writer.writerows(headlines)
    print(f"Exported to {filepath}")
def main():
    sources = load_sources()

    if os.path.exists(CACHE_FILE):
        print("Loading headlines from cache...")
        headlines = load_cached()
    else:
        print("Scraping news sites...")
        headlines = scrape_headlines(sources)
        cache_results(headlines)

    keyword = input("Enter a keyword to filter headlines: ").strip()
    filtered = filter_headlines(headlines, keyword)

    if filtered:
        display_table(filtered)

        choice = input("Do you want to export these results to CSV? (y/n): ").strip().lower()
        if choice == 'y':
            export_to_csv(filtered)
    else:
        print("No matching headlines found.")

if __name__ == "__main__":
    main()

import requests
import json
import os

# --- Load configuration from external file ---
with open("config.json") as f:
    cfg = json.load(f)

API_URL = cfg["API_URL"]   # pulled from config.json

# Subdirectory for output
OUTPUT_DIR = "current_pages"

# Ensure the directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

session = requests.Session()

def get_all_pages():
    """Fetch all page titles from the wiki."""
    titles = []
    apcontinue = None

    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "max",
            "format": "json"
        }
        if apcontinue:
            params["apcontinue"] = apcontinue

        res = session.get(API_URL, params=params).json()
        pages = res["query"]["allpages"]
        titles.extend([p["title"] for p in pages])

        if "continue" in res:
            apcontinue = res["continue"]["apcontinue"]
        else:
            break

    return titles

def get_page_content(title):
    """Fetch the wikitext of a single page."""
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
        "format": "json"
    }
    res = session.get(API_URL, params=params).json()
    pages = res["query"]["pages"]
    page = next(iter(pages.values()))
    if "revisions" in page:
        return page["revisions"][0]["*"]
    return ""

def sanitize_filename(name):
    """Make a safe filename from a page title."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

def main():
    titles = get_all_pages()
    print(f"Found {len(titles)} pages")

    for title in titles:
        content = get_page_content(title)
        filename = sanitize_filename(title) + ".txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"All pages saved into '{OUTPUT_DIR}' directory")

if __name__ == "__main__":
    main()


import requests
import json
import os

# --- Load configuration from external file ---
with open("config.json") as f:
    cfg = json.load(f)

API_URL = cfg["API_URL"]   # pulled from config.json

# Base directory for output
OUTPUT_DIR = "current_pages"

# Ensure base directory exists
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

def get_page_content_and_images(title):
    """Fetch the wikitext and images of a single page."""
    params = {
        "action": "query",
        "prop": "revisions|images",
        "rvprop": "content",
        "titles": title,
        "format": "json"
    }
    res = session.get(API_URL, params=params).json()
    pages = res["query"]["pages"]
    page = next(iter(pages.values()))

    content = ""
    images = []
    if "revisions" in page:
        content = page["revisions"][0]["*"]
    if "images" in page:
        images = [img["title"] for img in page["images"]]

    return content, images

def download_image(image_title, dest_folder):
    """Download an image file given its wiki title (e.g., 'File:Example.jpg')."""
    params = {
        "action": "query",
        "titles": image_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    res = session.get(API_URL, params=params).json()
    pages = res["query"]["pages"]
    page = next(iter(pages.values()))
    if "imageinfo" in page:
        url = page["imageinfo"][0]["url"]

        # Use the wiki reference name (File:Example.jpg) as filename
        safe_name = sanitize_filename(image_title.replace("File:", ""))

        filepath = os.path.join(dest_folder, safe_name)
        img_data = session.get(url).content
        with open(filepath, "wb") as f:
            f.write(img_data)
        print(f"Downloaded {safe_name}")

def sanitize_filename(name):
    """Make a safe filename from a page title or image name."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)

def main():
    titles = get_all_pages()
    print(f"Found {len(titles)} pages")

    for title in titles:
        content, images = get_page_content_and_images(title)

        # Create subfolder for this page
        page_folder = os.path.join(OUTPUT_DIR, sanitize_filename(title))
        os.makedirs(page_folder, exist_ok=True)

        # Save page text
        content_file = os.path.join(page_folder, "content.txt")
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Create images subfolder
        images_folder = os.path.join(page_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        # Download images
        for img in images:
            download_image(img, images_folder)

    print(f"All pages saved into '{OUTPUT_DIR}' with images in per-page subfolders")

if __name__ == "__main__":
    main()


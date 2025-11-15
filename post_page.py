import requests
import json
import os
import re
import sys

# --- Load configuration from external file (JSON) ---
with open("config.json") as f:
    config = json.load(f)

API_URL = config["API_URL"]      # e.g. "https://yourwiki.fandom.com/api.php"
USERNAME = config["USERNAME"]    # your Fandom username (or BotPassword username)
PASSWORD = config["PASSWORD"]    # your Fandom password (or BotPassword password)

# --- Start session ---
session = requests.Session()

# Step 1: Get login token
params = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json"
}
res = session.get(url=API_URL, params=params)
login_token = res.json()["query"]["tokens"]["logintoken"]

# Step 2: Log in
params = {
    "action": "login",
    "lgname": USERNAME,
    "lgpassword": PASSWORD,
    "lgtoken": login_token,
    "format": "json"
}
res = session.post(API_URL, data=params)
print("Login:", res.json())

# Step 3: Get CSRF token
params = {
    "action": "query",
    "meta": "tokens",
    "format": "json"
}
res = session.get(url=API_URL, params=params)
csrf_token = res.json()["query"]["tokens"]["csrftoken"]

# --- Read page content from file specified on command line ---
if len(sys.argv) < 2:
    print("Usage: python script.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]

with open(input_file, "r", encoding="utf-8") as f:
    page_content = f.read()

# --- Derive page title from input filename (without extension) ---
page_title = os.path.splitext(os.path.basename(input_file))[0]

# --- Find all [[File:...]] references ---
file_pattern = r"

\[

\[File:(.+?)(\|.*)?\]

\]+)"
matches = re.findall(file_pattern, page_content)

image_folder = "./images"

for match in matches:
    filename = match[0].strip()
    filepath = os.path.join(image_folder, filename)

    if not os.path.exists(filepath):
        print(f"Image {filename} not found in {image_folder}, skipping upload.")
        continue

    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "multipart/form-data")}
        params = {
            "action": "upload",
            "filename": filename,   # wiki filename will match local filename
            "token": csrf_token,
            "format": "json",
            "ignorewarnings": 1
        }
        res = session.post(API_URL, files=files, data=params)
        print(f"Upload {filename}:", res.json())

# --- Post the edit ---
params = {
    "action": "edit",
    "title": page_title,
    "token": csrf_token,
    "format": "json",
    "text": page_content,
    "summary": f"Automated edit from {input_file}: added content and uploaded images"
}
res = session.post(API_URL, data=params)
print("Edit:", res.json())


import requests
import json

# --- Load configuration from external file (JSON) ---
with open("config.json") as f:
    config = json.load(f)

API_URL = config["API_URL"]      # e.g. "https://yourwiki.fandom.com/api.php"
USERNAME = config["USERNAME"]    # your Fandom username
PASSWORD = config["PASSWORD"]    # your Fandom password

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

# Step 4: Define page content
page_title = "TEST"   # Replace with the page you want to edit

page_content = """
== Description ==
This is the description section.

== History ==
Details about history go here.

== Abilities ==
List of abilities.

== Archetypes ==
Archetype information.

== Notable Agents ==
Important agents listed here.

== References ==
<references />

"""

# Step 5: Post the edit
params = {
    "action": "edit",
    "title": page_title,
    "token": csrf_token,
    "format": "json",
    "text": page_content,
    "summary": "Automated edit: added structured sections and image"
}
res = session.post(API_URL, data=params)
print("Edit:", res.json())


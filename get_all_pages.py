import requests
import json

def list_all_pages(base_url, limit=500):
    """
    Lists all pages from a Fandom wiki using the MediaWiki API.

    Parameters:
    - wiki_domain: The subdomain of the Fandom wiki (e.g., 'marvel', 'starwars').
    - limit: Number of pages to fetch per request (max 500).

    Returns:
    - A list of page titles.
    """
    params = {
        'action': 'query',
        'list': 'allpages',
        'aplimit': limit,
        'format': 'json'
    }

    all_pages = []
    while True:
        response = requests.get(base_url, params=params)
        data = response.json()

        pages = data.get('query', {}).get('allpages', [])
        all_pages.extend([page['title'] for page in pages])

        if 'continue' in data:
            params.update(data['continue'])
        else:
            break

    return all_pages

# Example usage:
if __name__ == "__main__":
    with open("config.json") as f:
    	config = json.load(f)
    
    wiki = config["WIKI"]
    base_url = config["API_URL"]
    pages = list_all_pages(base_url)
    print(f"Total pages found: {len(pages)}")
    for title in pages:
        print(title)

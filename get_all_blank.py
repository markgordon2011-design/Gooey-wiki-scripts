import requests
from bs4 import BeautifulSoup4

def check_fandom_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching page: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for stub message
    stub_notice = soup.find(string=lambda text: text and "stub" in text.lower())
    if stub_notice:
        return "This page appears to be a stub."

    # Check for minimal content
    content = soup.find('div', {'class': 'mw-parser-output'})
    if not content or len(content.get_text(strip=True)) < 100:
        return "This page appears to be blank or nearly empty."

    return "This page has content and is not a stub."

# Example usage
url = "https://gooey-cube.fandom.com/api.php"
result = check_fandom_page(url)
print(result)

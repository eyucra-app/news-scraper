import requests
from bs4 import BeautifulSoup

# Fetch the page
url = "https://correodelsur.com/local"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Fetching URL:", url)
response = requests.get(url, headers=headers, timeout=10)
print("Status code:", response.status_code)
print("Content length:", len(response.text))

soup = BeautifulSoup(response.text, 'lxml')

# Check for uk-container
uk_containers = soup.find_all(class_='uk-container')
print(f"\n=== Found {len(uk_containers)} elements with class='uk-container' ===")

# Check with select
css_containers = soup.select('.uk-container')
print(f"=== Found {len(css_containers)} elements with selector '.uk-container' ===")

# Try just 'container'
containers = soup.find_all(class_='container')
print(f"=== Found {len(containers)} elements with class='container' ===")

# Check for h2 tags
all_h2 = soup.find_all('h2')
print(f"\n=== Found {len(all_h2)} h2 tags total ===")
if all_h2:
    print("First 3 h2 texts:")
    for h2 in all_h2[:3]:
        print(f"  - {h2.get_text(strip=True)[:80]}")

# Check for links with /local/
local_links = soup.find_all('a', href=lambda x: x and '/local/202' in x)
print(f"\n=== Found {len(local_links)} links with '/local/202' ===")
if local_links:
    print("First 3 local article links:")
    for link in local_links[:3]:
        print(f"  - href: {link.get('href')}")
        print(f"    text: {link.get_text(strip=True)[:80]}")

# Save a snippet of HTML for analysis
print("\n=== Saving HTML snippet ===")
with open('correodelsur_html_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text[:5000])
print("Saved first 5000 chars to correodelsur_html_debug.html")

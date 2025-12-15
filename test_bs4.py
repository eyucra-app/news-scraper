from bs4 import BeautifulSoup

# Test HTML
html = '<html><body><h2>Headline 1</h2><h2>Headline 2</h2><h2>Headline 3</h2></body></html>'
soup = BeautifulSoup(html, 'lxml')

# Test 1: Find body by tag name
container = soup.find('body')
print(f"Test 1 - Found body: {container is not None}")

if container:
    # Test 2: Find all h2 within body
    h2_tags = container.find_all('h2')
    print(f"Test 2 - Found {len(h2_tags)} h2 tags")
    
    for i, h2 in enumerate(h2_tags, 1):
        print(f"   {i}. {h2.get_text(strip=True)}")

print("\nNow testing with class-based container:")
html2 = '<html><div class="container"><h2>A</h2><h2>B</h2></div></html>'
soup2 = BeautifulSoup(html2, 'lxml')
container2 = soup2.find(class_="container")
print(f"Found container: {container2 is not None}")
if container2:
    h2s = container2.find_all('h2')
    print(f"Found {len(h2s)} h2 tags")

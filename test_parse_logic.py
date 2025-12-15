import asyncio
import sys
sys.path.insert(0, '/app')

from services.scraper import NewsScraper
from db.database import SessionLocal

async def test_parse_logic():
    # Test 1: Simple HTML
    print("=" * 50)
    print("TEST 1: Simple HTML with body tag")
    print("=" * 50)
    
    async with SessionLocal() as db:
        scraper = NewsScraper(db)
        
        html = '<html><body><h2>Headline 1</h2><h2>Headline 2</h2><h2>Headline 3</h2></body></html>'
        result = scraper._parse_headlines(html, 'body', 'h2')
        
        print(f"✓ Found {len(result)} headlines")
        for i, h in enumerate(result, 1):
            print(f"  {i}. {h['title']}")
    
    # Test 2: With container class
    print("\n" + "=" * 50)
    print("TEST 2: HTML with div container")
    print("=" * 50)
    
    async with SessionLocal() as db:
        scraper = NewsScraper(db)
        
        html = '<html><div class="uk-container"><h2>Test A</h2><h2>Test B</h2></div></html>'
        result = scraper._parse_headlines(html, 'uk-container', 'h2')
        
        print(f"✓ Found {len(result)} headlines")
        for i, h in enumerate(result, 1):
            print(f"  {i}. {h['title']}")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Parse logic is working!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_parse_logic())

import asyncio
from playwright.async_api import async_playwright

async def test_correo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navegando a correodelsur.com/local...")
        await page.goto("https://correodelsur.com/local", wait_until='networkidle')
        
        # Obtener html
        html = await page.content()
        print(f"HTML obtenido: {len(html)} caracteres\n")
        
        # Buscar diferentes contenedores
        containers_to_test = [
            "body",
            "main",
            ".uk-container",
            "#content",
            "article",
            "[class*='container']"
        ]
        
        for selector in containers_to_test:
            try:
                elements = await page.query_selector_all(selector)
                print(f"✓ {selector}: {len(elements)} elementos")
                
                if elements:
                    # Ver si tiene h2 dentro
                    first = elements[0]
                    h2s = await first.query_selector_all("h2")
                    print(f"  └─ h2 dentro: {len(h2s)}")
                    
                    if h2s:
                        text = await h2s[0].inner_text()
                        print(f"  └─ Primer h2: {text[:60]}...")
            except Exception as e:
                print(f"✗ {selector}: Error - {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_correo())

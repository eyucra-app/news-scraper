import asyncio
from playwright.async_api import async_playwright

async def analyze_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navegando a correodelsur.com/local...")
        await page.goto("https://correodelsur.com/local", wait_until='networkidle')
        
        # Obtener HTML
        html = await page.content()
        
        # Guardar a archivo
        with open('/tmp/correodelsur.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ HTML guardado: {len(html)} caracteres")
        
        # Buscar diferentes elementos
        print("\n=== Análisis de elementos ===")
        
        # Buscar h2
        h2_elements = await page.query_selector_all("h2")
        print(f"h2 tags: {len(h2_elements)}")
        if h2_elements:
            text = await h2_elements[0].inner_text()
            print(f"  Primer h2: {text[:80]}")
        
        # Buscar h5
        h5_elements = await page.query_selector_all("h5")
        print(f"\nh5 tags: {len(h5_elements)}")
        if h5_elements:
            for i, h5 in enumerate(h5_elements[:5], 1):
                text = await h5.inner_text()
                parent = await h5.evaluate('el => el.parentElement.tagName')
                print(f"  {i}. {text[:70]}... (parent: {parent})")
        
        # Buscar dentro de body
        body_h5 = await page.query_selector_all("body h5")
        print(f"\nbody > h5: {len(body_h5)}")
        
        # Buscar artículos o contenedores comunes
        articles = await page.query_selector_all("article")
        print(f"\narticle tags: {len(articles)}")
        
        sections = await page.query_selector_all("section")
        print(f"section tags: {len(sections)}")
        
        await browser.close()
        print("\n✓ Análisis completado")

if __name__ == "__main__":
    asyncio.run(analyze_html())

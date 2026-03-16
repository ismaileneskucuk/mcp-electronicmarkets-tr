import asyncio
import sys
from fastmcp import FastMCP
from app.scrapers.robocombo import RobocomboScraper
from app.scrapers.robotistan import RobotistanScraper

mcp = FastMCP("ElectronicMarkets-TR")

@mcp.tool()
async def search_in_markets(product_name: str):
    """
    Searches for electronic components in Turkish markets (Robocombo, Robotistan) 
    by product name. Returns a list of products sorted by price.
    """
    scrapers = [
        RobocomboScraper(),
        #RobotistanScraper()
    ]
    
    tasks = [scraper.scrape(product_name) for scraper in scrapers]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for res in responses:
        if isinstance(res, list):
            all_results.extend(res)
        else:
            print(f"Error during scraping: {res}", file=sys.stderr)
            
    return sorted(all_results, key=lambda x: (not x.stock_status, x.price))

# DOSYANIN EN ALTINA EKLE (TEST İÇİN)
async def test_run():
    print("--- TEST BAŞLADI: Robocombo taranıyor... ---")
    results = await search_in_markets("arduino")
    if not results:
        print("Sonuç bulunamadı veya bir hata oluştu.")
    for r in results:
        status = "VAR" if r.stock_status else "YOK"
        print(f"[{status}] {r.name} - {r.price} TL")
    print("--- TEST BİTTİ ---")

if __name__ == "__main__":
    # mcp.run() # <--- Bunu geçici olarak yorum satırı yap (başına # koy)
    asyncio.run(test_run()) # Direkt fonksiyonu çalıştır
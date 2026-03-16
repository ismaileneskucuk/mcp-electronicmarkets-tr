import asyncio
import sys
from fastmcp import FastMCP
from app.scrapers.robocombo import RobocomboScraper

# 1. Sunucumuzu Tanımlıyoruz
# İsmi ne kadar net olursa, AI o kadar iyi anlar ne işe yaradığını.
mcp = FastMCP("ElectronicMarkets-TR")

# 2. Aracı (Tool) Tanımlıyoruz
# @mcp.tool() dekoratörü, AI'ya "Bu fonksiyonu sen kullanabilirsin" der.
@mcp.tool()
async def search_in_markets(product_name: str):
    """
    Searches for electronic components in Turkish markets (Robocombo, etc.) 
    by product name. Returns a list of products with their price, 
    stock status, and URL.
    """
    # İleride buraya daha fazla scraper ekleyeceğiz (Robotistan, Direnc vb.)
    scrapers = [
        RobocomboScraper(),
        # Buraya yeni scraperlar gelecek...
    ]
    
    # Tüm siteleri aynı anda (paralel) taramak için görev listesi oluşturuyoruz
    tasks = [scraper.scrape(product_name) for scraper in scrapers]
    
    # Matematik Mühendisliği farkı: asyncio.gather ile tüm siteleri 
    # tek tek beklemek yerine AYNI ANDA tarıyoruz. Hız = 5x!
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for res in responses:
        if isinstance(res, list):
            all_results.extend(res)
        else:
            # Hataları sadece stderr'e basıyoruz (AI görmesin, biz görelim)
            print(f"Tarama sırasında hata oluştu: {res}", file=sys.stderr)
            
    # En ucuz olanı en üste getirelim (Sorting)
    # x.price'a göre küçükten büyüye sıralıyoruz.
    sorted_results = sorted(all_results, key=lambda x: x.price)
    
    return sorted_results

if __name__ == "__main__":
    mcp.run()
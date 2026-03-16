import asyncio
import sys
from fastmcp import FastMCP
from app.scrapers.robocombo import RobocomboScraper
from app.scrapers.robotistan import RobotistanScraper
from app.scrapers.direnc import DirencScraper

mcp = FastMCP("ElectronicMarkets-TR")

@mcp.tool()
async def search_in_markets(product_name: str, only_in_stock: bool = True):
    """
    Searches for electronic components in Turkish markets (Robocombo, Robotistan, Direnc.net).
    Returns a sorted list of products by price.
    """
    scrapers = [
        RobocomboScraper(),
        RobotistanScraper(),
        DirencScraper()
    ]
    
    tasks = [scraper.scrape(product_name) for scraper in scrapers]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for res in responses:
        if isinstance(res, list):
            all_results.extend(res)
        else:
            print(f"Scraping error: {res}", file=sys.stderr)
            
    if only_in_stock:
        all_results = [p for p in all_results if p.stock_status]
            
    return sorted(all_results, key=lambda x: x.price)

async def test_run():
    print("--- STARTING MULTI-MARKET SEARCH ---")
    # Set only_in_stock=True for cleaner testing
    results = await search_in_markets("arduino", only_in_stock=True)
    
    if not results:
        print("No results found.")
        
    for r in results:
        print(f"[{r.site}] {r.name} - {r.price} TL")
    
    print(f"\nTotal products found: {len(results)}")
    print("--- SEARCH FINISHED ---")

if __name__ == "__main__":
    # mcp.run() # For production server
    asyncio.run(test_run()) # For local testing
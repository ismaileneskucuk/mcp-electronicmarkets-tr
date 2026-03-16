import asyncio
import sys
from fastmcp import FastMCP
from app.scrapers.robocombo import RobocomboScraper
from app.scrapers.robotistan import RobotistanScraper
from app.scrapers.direnc import DirencScraper
from app.scrapers.robo90 import Robo90Scraper

mcp = FastMCP("ElectronicMarkets-TR")

@mcp.tool()
async def search_in_markets(product_name: str, only_in_stock: bool = True):
    """
    Searches for electronic components in Turkish markets (Robocombo, Robotistan, Direnc.net, Robo90).
    :param product_name: Name of the product to search.
    :param only_in_stock: If True, only products available for purchase are returned.
    :return: A list of products sorted by price (cheapest first).
    """
    scrapers = [
        RobocomboScraper(),
        RobotistanScraper(),
        DirencScraper(),
        Robo90Scraper()
    ]
    
    # Run all scrapers concurrently for maximum performance
    tasks = [scraper.scrape(product_name) for scraper in scrapers]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for res in responses:
        if isinstance(res, list):
            all_results.extend(res)
        else:
            print(f"Error during scraping process: {res}", file=sys.stderr)
            
    # Apply stock filter if requested
    if only_in_stock:
        all_results = [p for p in all_results if p.stock_status]
            
    # Global sorting by price across all markets
    return sorted(all_results, key=lambda x: x.price)

async def test_run():
    print("--- STARTING QUAD-MARKET SEARCH ---")
    query = "arduino uno"
    results = await search_in_markets(query, only_in_stock=True)
    
    if not results:
        print(f"No available products found for '{query}'.")
        return

    for r in results:
        print(f"[{r.site}] {r.name} - {r.price} TL")
    
    print(f"\nTotal available products from 4 markets: {len(results)}")
    print("--- SEARCH COMPLETED ---")

if __name__ == "__main__":
    # mcp.run() # Use for real MCP server mode
    asyncio.run(test_run()) # Use for local debugging
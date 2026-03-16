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
    Retrieves RAW product data from Turkish electronics markets (Robocombo, Robotistan, Direnc.net, Robo90).
    
    :param product_name: The target product name or keywords to search for in the markets.
    :param only_in_stock: If True (default), filters out products that are currently out of stock.
    
    Note: Results are provided in their raw state from the first search pages. 
    The AI must evaluate relevance and sort the final list for the user.
    """
    clean_query = product_name.strip()
    scrapers = [
        RobocomboScraper(),
        RobotistanScraper(),
        DirencScraper(),
        Robo90Scraper()
    ]
    
    # Concurrent fetching
    tasks = [scraper.scrape(clean_query) for scraper in scrapers]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    unique_results = {}
    for res in responses:
        if isinstance(res, list):
            for p in res:
                # Deduplication by URL
                if p.url not in unique_results:
                    unique_results[p.url] = p
        else:
            # Output errors to stderr so they don't break the JSON response
            print(f"Scraper Error: {res}", file=sys.stderr)
            
    final_list = list(unique_results.values())
    
    # Basic stock filtering
    if only_in_stock:
        final_list = [p for p in final_list if p.stock_status]
            
    return final_list

if __name__ == "__main__":
    mcp.run()
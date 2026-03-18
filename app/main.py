import os
import asyncio
import httpx
import logging
from fastmcp import FastMCP
from app.scrapers.robocombo import RobocomboScraper
from app.scrapers.robotistan import RobotistanScraper
from app.scrapers.direnc import DirencScraper
from app.scrapers.robo90 import Robo90Scraper

# Setup logging
base_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(base_dir, "mcp_server.log")
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ElectronicMarkets")

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
    
    # Concurrent fetching with shared connection pool
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        tasks = [scraper.scrape(client, logger, clean_query) for scraper in scrapers]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    unique_results = {}
    for res in responses:
        if isinstance(res, list):
            for p in res:
                # Deduplication by URL
                if p.url not in unique_results:
                    unique_results[p.url] = p
        else:
            # Output errors to log file
            logger.error(f"Scraper Exception: {res}")
            
    final_list = list(unique_results.values())
    
    # Basic stock filtering
    if only_in_stock:
        final_list = [p for p in final_list if p.stock_status]
            
    return final_list

@mcp.tool()
async def batch_search_in_markets(product_names: list[str], only_in_stock: bool = True) -> dict:
    """
    CRITICAL (NOTE FOR AI): When you need to search for multiple products (e.g., a shopping cart list), you MUST use THIS FUNCTION INSTEAD of calling `search_in_markets` in a loop. It is significantly faster because it searches the entire list concurrently.
    
    Retrieves RAW product data from Turkish electronics markets for MULTIPLE queries simultaneously.
    
    :param product_names: A list of the product names or keywords to search for (e.g., ["arduino uno", "bno055", "esp32"]).
    :param only_in_stock: If True (default), filters out products that are currently out of stock.
    :return: A dictionary where each key is the product query, and the value is a list of product results for that query.
    """
    clean_queries = [name.strip() for name in product_names if name.strip()]
    if not clean_queries:
        return {}
        
    # Run search_in_markets as an asynchronous task for each query
    tasks = [search_in_markets(query, only_in_stock) for query in clean_queries]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    results_by_query = {}
    for query, res in zip(clean_queries, responses):
        if isinstance(res, Exception):
            logger.error(f"Batch search error for {query}: {res}")
            results_by_query[query] = []
        else:
            # search_in_markets returns a list containing ProductModel objects
            results_by_query[query] = res
            
    return results_by_query

if __name__ == "__main__":
    mcp.run()
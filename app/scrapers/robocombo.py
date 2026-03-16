import json
import httpx
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class RobocomboScraper(BaseScraper):
    """Scraper for Robocombo.com using their internal JSON API for better reliability."""

    async def scrape(self, query: str) -> list[ProductModel]:
        """
        Fetches products from Robocombo by directly calling their product API.
        Supports multi-page crawling.
        """
        all_results = []
        page_num = 1
        MAX_PAGES = 10  # Safety limit to prevent long wait times
        
        while page_num <= MAX_PAGES:
            # The internal API endpoint you discovered
            api_url = "https://www.robocombo.com/api/product/GetProductList"
            
            # Replicating the filter structure from your links
            filter_json = {
                "SearchKeyword": query,
                "MinPrice": 0,
                "MaxPrice": 0,
                "IsInStock": False,
                "IsPriceRequest": True,
                "IsProductListPage": True,
                "NonStockShowEnd": 1
            }
            
            paging_json = {
                "PageItemCount": 0, # 0 means use site default (usually 48)
                "PageNumber": page_num,
                "OrderBy": "SMARTSORTING",
                "OrderDirection": "DESC"
            }

            # Query parameters for the GET request
            params = {
                "c": "trtry0000",
                "FilterJson": json.dumps(filter_json),
                "PagingJson": json.dumps(paging_json),
                "PageType": 10
            }

            try:
                # We use httpx directly to get the JSON response
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(api_url, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                products = data.get("products", [])
                
                # Stop if the current page has no products
                if not products:
                    break
                
                for p in products:
                    # API returns clean data, no need for complex CSS selectors
                    name = p.get("name", "")
                    link = "https://www.robocombo.com" + p.get("url", "")
                    
                    # Using the price string with currency for our clean_price helper
                    price_str = p.get("productSellPriceStr", "0")
                    price = self.clean_price(price_str)
                    
                    # 'inStock' is a boolean returned directly by the API
                    stock = p.get("inStock", False)
                    
                    all_results.append(ProductModel(
                        site="Robocombo",
                        name=name,
                        price=price,
                        stock_status=stock,
                        url=link
                    ))
                
                # Check if we have reached the total count to stop early
                total_count = data.get("totalProductCount", 0)
                if len(all_results) >= total_count:
                    break

                page_num += 1
                
            except Exception as e:
                print(f"Robocombo Page {page_num} Error: {e}", file=sys.stderr)
                break
                
        return all_results
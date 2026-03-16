import json
import httpx
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class RobocomboScraper(BaseScraper):
    """Scraper for Robocombo.com with correct discount price detection."""

    async def scrape(self, query: str) -> list[ProductModel]:
        all_results = []
        page_num = 1
        
        while page_num <= self.max_pages:
            api_url = "https://www.robocombo.com/api/product/GetProductList"
            
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
                "PageItemCount": 0,
                "PageNumber": page_num,
                "OrderBy": "SMARTSORTING",
                "OrderDirection": "DESC"
            }

            params = {
                "c": "trtry0000",
                "FilterJson": json.dumps(filter_json),
                "PagingJson": json.dumps(paging_json),
                "PageType": 10
            }

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(api_url, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                products = data.get("products", [])
                if not products:
                    break
                
                for p in products:
                    name = p.get("name", "")
                    link = "https://www.robocombo.com" + p.get("url", "")
                    
                    # --- SMART PRICE DETECTION ---
                    # We check both Cart Price and Sell Price and pick the lowest non-zero value.
                    # productCartPriceStr is typically the final discounted price in Ticimax API.
                    price_options = [
                        p.get("productCartPriceStr"),
                        p.get("productSellPriceStr"),
                        p.get("productPriceOriginalStr")
                    ]
                    
                    # Convert all potential prices to floats using our base helper
                    cleaned_prices = [self.clean_price(pr) for pr in price_options if pr]
                    
                    # Pick the minimum price that is greater than 0
                    price = min([cp for cp in cleaned_prices if cp > 0]) if cleaned_prices else 0.0
                    
                    stock = p.get("inStock", False)
                    
                    all_results.append(ProductModel(
                        site="Robocombo",
                        name=name,
                        price=price,
                        stock_status=stock,
                        url=link
                    ))
                
                total_count = data.get("totalProductCount", 0)
                if len(all_results) >= total_count:
                    break

                page_num += 1
                
            except Exception as e:
                print(f"Robocombo Page {page_num} Error: {e}", file=sys.stderr)
                break
                
        return all_results
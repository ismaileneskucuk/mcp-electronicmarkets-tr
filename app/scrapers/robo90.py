from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class Robo90Scraper(BaseScraper):
    """Scraper for Robo90.com with multi-page support."""

    async def scrape(self, query: str) -> list[ProductModel]:
        """
        Scrapes Robo90 products across multiple pages based on the search query.
        """
        all_results = []
        page_num = 1
        MAX_PAGES = 10  # Standard limit for AI response time
        
        while page_num <= MAX_PAGES:
            # URL structure using the 'pg' parameter for pagination
            url = f"https://www.robo90.com/arama?q={query}&pg={page_num}"
            
            try:
                soup = await self.get_soup(url)
                items = soup.select(".productItem")
                
                # If no products found on current page, stop crawling
                if not items:
                    break
                
                for item in items:
                    title_tag = item.select_one(".listProductName")
                    if not title_tag:
                        continue
                    
                    name = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    if not link.startswith("http"):
                        link = "https://www.robo90.com" + link
                    
                    price_tag = item.select_one(".currentPrice")
                    price = self.clean_price(price_tag.get_text(strip=True) if price_tag else "0")
                    
                    # Logic: If 'out-of-stock' class exists, the item is unavailable
                    is_out_of_stock = item.select_one(".out-of-stock")
                    stock = False if is_out_of_stock else True
                    
                    all_results.append(ProductModel(
                        site="Robo90",
                        name=name,
                        price=price,
                        stock_status=stock,
                        url=link
                    ))
                
                page_num += 1
                
            except Exception as e:
                print(f"Robo90 Page {page_num} Error: {e}", file=sys.stderr)
                break
                
        return all_results
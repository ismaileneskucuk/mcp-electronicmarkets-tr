from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class Robo90Scraper(BaseScraper):
    """Scraper for Robo90.com using the dynamic product loader service."""

    async def scrape(self, query: str) -> list[ProductModel]:
        """
        Scrapes Robo90 products using their internal loader to handle dynamic content.
        """
        all_results = []
        page_num = 1
        
        while page_num <= self.max_pages:
            # Robo90 uses the same T-Soft loader structure as Direnc.net
            url = f"https://www.robo90.com/srv/service/product/loader?arama&q={query}&link=arama&pg={page_num}"
            
            try:
                soup = await self.get_soup(url)
                
                # Based on the HTML you provided, each item is a 'productItem'
                items = soup.select(".productItem")
                
                if not items:
                    break
                
                for item in items:
                    # Extract name and link from 'listProductName'
                    title_tag = item.select_one(".listProductName")
                    if not title_tag:
                        continue
                        
                    name = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    if not link.startswith("http"):
                        link = "https://www.robo90.com" + link
                    
                    # Extract price from 'currentPrice'
                    price_tag = item.select_one(".currentPrice")
                    price = self.clean_price(price_tag.get_text(strip=True) if price_tag else "0")
                    
                    # Stock logic: T-Soft sites use 'out-of-stock' class for missing items
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
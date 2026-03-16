from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class DirencScraper(BaseScraper):
    """Scraper for Direnc.net using the specialized product loader endpoint."""

    async def scrape(self, query: str) -> list[ProductModel]:
        """
        Scrapes Direnc.net products across multiple pages using their dynamic loader service.
        """
        all_results = []
        page_num = 1
        
        while page_num <= self.max_pages:
            # Using the specialized loader URL you provided
            url = f"https://www.direnc.net/srv/service/product/loader?arama&q={query}&link=arama&pg={page_num}"
            
            try:
                soup = await self.get_soup(url)
                
                # Each product is wrapped in a 'productItem' class
                items = soup.select(".productItem")
                
                # If no items are found, we've reached the end of results
                if not items:
                    break
                
                for item in items:
                    # Extract title and link
                    title_tag = item.select_one(".productDescription")
                    if not title_tag:
                        continue
                        
                    name = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    if not link.startswith("http"):
                        link = "https://www.direnc.net" + link
                    
                    # Extract price from the currentPrice span
                    price_tag = item.select_one(".currentPrice")
                    price = self.clean_price(price_tag.get_text(strip=True) if price_tag else "0")
                    
                    # Logic: If 'out-of-stock' span exists, item is unavailable
                    out_of_stock_tag = item.select_one(".out-of-stock")
                    stock = False if out_of_stock_tag else True
                    
                    all_results.append(ProductModel(
                        site="Direnc.net",
                        name=name,
                        price=price,
                        stock_status=stock,
                        url=link
                    ))
                
                # Move to the next page
                page_num += 1
                
            except Exception as e:
                print(f"Direnc.net Page {page_num} Error: {e}", file=sys.stderr)
                break
                
        return all_results
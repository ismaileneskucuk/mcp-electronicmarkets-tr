from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel
import sys

class RobotistanScraper(BaseScraper):
    """Scraper for Robotistan.com with multi-page support."""

    async def scrape(self, query: str) -> list[ProductModel]:
        """
        Scrapes product data across multiple pages based on the search query.
        """
        all_results = []
        page_num = 1
        MAX_PAGES = 10
        
        while page_num <= MAX_PAGES:
            # URL with pagination parameter
            url = f"https://www.robotistan.com/arama?q={query}&pg={page_num}"
            
            try:
                soup = await self.get_soup(url)
                items = soup.select(".product-item")
                
                # Stop if no items are found on the current page
                if not items:
                    break
                
                for item in items:
                    title_tag = item.select_one(".product-title")
                    if not title_tag:
                        continue
                    
                    name = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    if not link.startswith("http"):
                        link = "https://www.robotistan.com" + link
                    
                    price_tag = item.select_one(".product-price")
                    price = self.clean_price(price_tag.get_text(strip=True) if price_tag else "0")
                    
                    # Logic: If add-to-cart button exists, item is in stock
                    stock = True if item.select_one(".add-to-cart-btn") else False
                    
                    all_results.append(ProductModel(
                        site="Robotistan",
                        name=name,
                        price=price,
                        stock_status=stock,
                        url=link
                    ))
                
                # Increment page number to crawl the next page
                page_num += 1
                
            except Exception as e:
                print(f"Robotistan Page {page_num} Error: {e}", file=sys.stderr)
                break
                
        return all_results
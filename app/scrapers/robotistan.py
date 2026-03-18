import logging
import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel

class RobotistanScraper(BaseScraper):
    """Scraper for Robotistan.com fetching the single first page."""

    async def scrape(self, client: httpx.AsyncClient, logger: logging.Logger, query: str) -> list[ProductModel]:
        """Scrapes the first page of Robotistan.com search results."""
        all_results = []
        url = f"https://www.robotistan.com/arama?q={query}"
        
        try:
            soup = await self.get_soup(client, url)
            
            items = soup.select(".product-item")
            
            for item in items:
                title_tag = item.select_one(".product-title")
                if not title_tag:
                    continue
                
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.robotistan.com" + link
                
                price_tag = item.select_one(".product-price")
                price = self.clean_price(price_tag.get_text() if price_tag else "0")
                
                # If an add-to-cart button exists, item is in stock
                stock = True if item.select_one(".add-to-cart-btn") else False
                
                all_results.append(ProductModel(
                    site="Robotistan",
                    name=name,
                    price=price,
                    stock_status=stock,
                    url=link
                ))
                
        except Exception as e:
            logger.error(f"Robotistan Error: {e}")
            
        return all_results
import logging
import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel

class Robo90Scraper(BaseScraper):
    """Scraper for Robo90.com using frontend search without pagination."""

    async def scrape(self, client: httpx.AsyncClient, logger: logging.Logger, query: str) -> list[ProductModel]:
        """Scrapes the first page of Robo90.com search results."""
        all_results = []
        url = f"https://www.robo90.com/arama?q={query}"
        
        try:
            soup = await self.get_soup(client, url)
            
            # Use universal selectors to catch different e-commerce layouts
            items = soup.select(".productItem")
            
            for item in items:
                title_tag = item.select_one(".listProductName")
                if not title_tag:
                    continue
                    
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.robo90.com" + link
                
                # Fetch price
                price_tag = item.select_one(".currentPrice")
                price = self.clean_price(price_tag.get_text() if price_tag else "0")
                
                # Check for out-of-stock indicators
                stock_tag = item.select_one(".out-of-stock")
                stock = False if stock_tag else True
                
                all_results.append(ProductModel(
                    site="Robo90",
                    name=name,
                    price=price,
                    stock_status=stock,
                    url=link
                ))
                
        except Exception as e:
            logger.error(f"Robo90 Error: {e}")
            
        return all_results
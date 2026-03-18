import logging
import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel

class DirencScraper(BaseScraper):
    """Scraper for Direnc.net."""

    async def scrape(self, client: httpx.AsyncClient, logger: logging.Logger, query: str) -> list[ProductModel]:
        """Scrapes the first page of Direnc.net search results."""
        all_results = []
        url = f"https://www.direnc.net/arama?q={query}"
        
        try:
            soup = await self.get_soup(client, url)
            
            # Find product containers
            items = soup.select(".productKapsa")
            
            for item in items:
                title_tag = item.select_one(".productDescription")
                if not title_tag:
                    continue
                    
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.direnc.net" + link
                
                # Fetch price
                price_tag = item.select_one(".currentPrice")
                price = self.clean_price(price_tag.get_text() if price_tag else "0")
                
                # Check for out-of-stock indicators
                stock_tag = item.select_one("out-of-stock")
                stock = False if stock_tag else True
                
                all_results.append(ProductModel(
                    site="Direnc.net",
                    name=name,
                    price=price,
                    stock_status=stock,
                    url=link
                ))
                
        except Exception as e:
            logger.error(f"Direnc.net Error: {e}")
            
        return all_results
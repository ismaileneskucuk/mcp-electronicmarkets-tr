import logging
import httpx
from app.scrapers.base import BaseScraper
from app.models import ProductModel

class RobocomboScraper(BaseScraper):
    """Scraper for Robocombo.com using frontend search without pagination."""

    async def scrape(self, client: httpx.AsyncClient, logger: logging.Logger, query: str) -> list[ProductModel]:
        all_results = []
        url = f"https://www.robocombo.com/Arama?1&kelime={query}"
        
        try:
            soup = await self.get_soup(client, url)
            
            # Find product containers using robust selectors
            items = soup.select(".productItem")
            
            for item in items:
                title_tag = item.select_one(".productName a")
                if not title_tag:
                    continue
                    
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.robocombo.com" + link
                
                # Fetch price from potential tags
                price_tag = item.select_one(".discountPriceSpan")
                price = self.clean_price(price_tag.get_text() if price_tag else "0")
                
                # Determine stock status
                stock_tag = item.select_one(".TukendiIco")
                stock = False if stock_tag else True
                
                all_results.append(ProductModel(
                    site="Robocombo",
                    name=name,
                    price=price,
                    stock_status=stock,
                    url=link
                ))
                
        except Exception as e:
            logger.error(f"Robocombo Error: {e}")
            
        return all_results
import httpx
from abc import ABC, abstractmethod
from app.models import ProductModel
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    def __init__(self):
        # Default pagination limit for high relevance
        self.max_pages = 1
        # Standard headers to mimic a real browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/"
        }

    @abstractmethod
    async def scrape(self, query: str) -> list[ProductModel]:
        """Each subclass must implement this method to perform site-specific scraping."""
        pass

    async def get_soup(self, url: str) -> BeautifulSoup:
        """Helper method to fetch HTML and return a BeautifulSoup object."""
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')

    def clean_price(self, price_str: str) -> float:
        """Helper method to clean Turkish currency strings and convert to float."""
        if not price_str:
            return 0.0
        # "3.842,55 ₺" -> 3842.55
        clean = price_str.replace("₺", "").replace("TL", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(clean)
        except ValueError:
            return 0.0
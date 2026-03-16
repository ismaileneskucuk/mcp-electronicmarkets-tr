import httpx
from abc import ABC, abstractmethod
from app.models import ProductModel
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    def __init__(self):
        # Gerçek bir tarayıcı gibi görünmek için Header
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @abstractmethod
    async def scrape(self, query: str) -> list[ProductModel]:
        """Her alt sınıf bu metodu kendine göre doldurmak zorundadır."""
        pass

    async def get_soup(self, url: str) -> BeautifulSoup:
        """Ortak HTML çekme ve Soup objesi oluşturma metodu."""
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status() # Hata varsa fırlatır
            return BeautifulSoup(response.text, 'html.parser')

    def clean_price(self, price_str: str) -> float:
        """Fiyat metnini temizleyip float'a çeviren ortak yardımcı metot."""
        if not price_str:
            return 0.0
        # "263,44 ₺" -> 263.44
        clean = price_str.replace("₺", "").replace("TL", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(clean)
        except ValueError:
            return 0.0
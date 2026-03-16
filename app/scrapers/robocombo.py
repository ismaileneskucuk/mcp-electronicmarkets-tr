from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.models import ProductModel

class RobocomboScraper(BaseScraper):
    async def scrape(self, query: str) -> list[ProductModel]:
        # Robocombo arama URL'si (query parametresiyle)
        url = f"https://www.robocombo.com/Arama?1&kelime={query}"
        
        try:
            # Base class'taki get_soup metodunu kullanarak HTML'i çekiyoruz
            soup = await self.get_soup(url)
            results = []
            
            # Ürün kutucuklarını seç (ItemOrj class'lı divler)
            items = soup.select("div.ItemOrj")
            
            for item in items:
                # Ürün Adı ve Linki çekme
                name_tag = item.select_one(".productName a")
                if not name_tag: continue
                
                name = name_tag.text.strip()
                link = name_tag['href']
                if not link.startswith("http"):
                    link = "https://www.robocombo.com" + link
                
                # Fiyatı çekme ve temizleme (Base class'taki metotla)
                price_tag = item.select_one(".discountPriceSpan")
                price_text = price_tag.text if price_tag else "0"
                price = self.clean_price(price_text)
                
                # Stok Durumu (TukendiIco varsa stok yoktur)
                is_out_of_stock = item.select_one(".TukendiIco")
                stock = False if is_out_of_stock else True
                
                # Veriyi Pydantic modelimize uygun şekilde paketliyoruz
                results.append(ProductModel(
                    site="Robocombo",
                    name=name,
                    price=price,
                    stock_status=stock,
                    url=link
                ))
                
            return results
            
        except Exception as e:
            # Hataları stderr'e basıyoruz ki MCP protokolü bozulmasın
            import sys
            print(f"Robocombo Scraper Hatası ({query}): {e}", file=sys.stderr)
            return []
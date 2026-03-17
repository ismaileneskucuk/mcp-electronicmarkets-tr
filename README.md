# Electronic Markets TR - MCP Server

Bu proje, Türkiye'nin önde gelen elektronik bileşen marketlerinde (Robotistan, Robocombo, Direnc.net, Robo90) aynı anda ürün, fiyat ve stok araması yapmanızı sağlayan bir **MCP (Model Context Protocol)** sunucusudur. 

Yapay zeka modellerinin (Claude, Gemini vb.) Türkiye yerel piyasasından gerçek zamanlı veri çekerek, en uygun fiyatlı ve stokta bulunan ürünleri bulmasına yardımcı olur.

## 🚀 Özellikler

* **Geniş Kapsam:** Tek bir sorgu ile 4 farklı mağazadan (Robotistan, Robocombo, Direnc.net, Robo90) veri toplar.
* **Doğru Fiyatlandırma:** Robocombo gibi sitelerdeki indirimli (nihai) fiyatları otomatik olarak yakalar.
* **Dinamik Veri Çekme:** Robo90 ve Direnc.net gibi dinamik yükleme yapan sitelerin loader servislerini kullanarak en güncel veriye ulaşır.
* **Hız ve Optimizasyon:** Paralel sorgulama sayesinde milisaniyeler içinde sonuç döndürür. Gereksiz veri yükünden kaçınmak için sayfa limitleri ve veri tekilleştirme uygulanmıştır.
* **AI Odaklı Mimari:** Veriler ham olarak AI'ya sunulur; alaka düzeyi ve sıralama işlemleri AI'nın muhakeme yeteneğine bırakılmıştır.

## 🛠 Desteklenen Marketler

| Market | Durum | Özellik |
| :--- | :--- | :--- |
| **Robotistan** | ✅ Aktif | Kategori bazlı geniş arama. |
| **Robocombo** | ✅ Aktif | Sepetteki indirimli fiyat tespiti. |
| **Direnc.net** | ✅ Aktif | Loader servisi üzerinden hızlı veri. |
| **Robo90** | ✅ Aktif | Dinamik loader üzerinden yüksek isabetli arama. |

## 📦 Kurulum

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/ismaileneskucuk/mcp-electronicmarkets-tr.git
   cd mcp-electronicmarkets-tr
   ```

2. **Sanal ortam oluşturun ve kütüphaneleri kurun:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows için
   source venv/bin/activate  # Linux/Mac için
   pip install .
   ```

## 🤖 Claude Desktop Entegrasyonu

Claude Desktop'ta kullanabilmek için `claude_desktop_config.json` dosyanıza aşağıdaki yapılandırmayı ekleyin:

```json
{
  "mcpServers": {
    "electronic-markets-tr": {
      "command": "C:/PROJE_DIZINI/mcp-electronicmarkets-tr/venv/Scripts/python.exe",
      "args": [
        "C:/PROJE_DIZINI/mcp-electronicmarkets-tr/app/main.py"
      ]
    }
  }
}
```
*(Not: Windows için venv/Scripts/python.exe, Mac/Linux için venv/bin/python yolu verilmelidir.)*

## 💡 Kullanım Örnekleri

Sunucu aktif olduğunda Claude veya Gemini'a şu tarz sorular sorabilirsiniz:
* "Arduino Uno R3 klon için 4 marketi tara, en ucuz ve stokta olanı bul."
* "Raspberry Pi 5 8GB fiyatlarını karşılaştır ve kargo avantajı olanı söyle."
* "BMP280 sensörü hangi mağazalarda stokta var?"

## 📝 Geliştirme Notu
Bu proje, **Gemini** ve **Claude** yapay zeka modelleri ile "pair-programming" yapılarak geliştirilmiştir. Yazılım mimarisi ve mağaza özelindeki veri çekme mantığı, yapay zekanın en verimli şekilde işleyebileceği "data pipeline" prensipleriyle optimize edilmiştir.

## ⚖️ Lisans
Bu proje **MIT License** ile lisanslanmıştır.

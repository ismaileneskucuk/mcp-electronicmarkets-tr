# app/models.py dosyası
from pydantic import BaseModel, HttpUrl

class ProductModel(BaseModel):
    site: str
    name: str
    price: float
    stock_status: bool
    url: HttpUrl
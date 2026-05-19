import asyncio
import random
from datetime import datetime, timedelta, date
import httpx
from models.database import AsyncSessionLocal, Product, PriceHistory, TrendingProduct

async def fetch_fake_products():
    """DummyJSON API üzerinden sahte ürün verilerini çeker."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://dummyjson.com/products?limit=50")
            if response.status_code == 200:
                data = response.json()
                return data.get("products", [])
    except Exception as e:
        print(f"Fake API'den veri çekilemedi: {e}")
    return []

def map_category(fake_cat):
    """API'den gelen kategorileri sistemimizin kategorilerine dönüştürür."""
    cat_mapping = {
        "smartphones": "Elektronik",
        "laptops": "Elektronik",
        "tablets": "Elektronik",
        "mobile-accessories": "Elektronik",
        "fragrances": "Güzellik",
        "skincare": "Güzellik",
        "beauty": "Güzellik",
        "groceries": "Ev & Yaşam",
        "home-decoration": "Ev & Yaşam",
        "furniture": "Ev & Yaşam",
        "kitchen-accessories": "Ev & Yaşam",
        "sports-accessories": "Spor & Fitness",
        "mens-shoes": "Spor & Fitness",
    }
    return cat_mapping.get(fake_cat, "Genel")

async def seed_database():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(Product))
        count = result.scalar()
        if count and count > 0:
            return  # Veritabanı zaten doluysa tekrar ekleme yapma

        print("Sahte API (DummyJSON) üzerinden ürünler çekiliyor ve veritabanı oluşturuluyor...")
        today = date.today()
        fake_products = await fetch_fake_products()
        
        if not fake_products:
            print("Sahte ürünler çekilemedi. Veritabanı tohumlanmadı.")
            return

        for dp in fake_products:
            supplier_p = float(dp.get("price", 10.0))
            # Satış fiyatını tedarik fiyatının 2 ile 4 katı arasında simüle et (Dropshipping mantığı)
            market_p = round(supplier_p * random.uniform(2.0, 4.0), 2)
            roi = round(((market_p - supplier_p) / supplier_p) * 100, 1)
            
            p_data = {
                "name": dp.get("title", "İsimsiz Ürün"),
                "category": map_category(dp.get("category", "genel")),
                "image_url": dp.get("thumbnail", ""),
                "supplier_price": round(supplier_p, 2),
                "market_price": market_p,
                "trend_score": int(random.uniform(70, 98)),
                "roi_percent": roi,
                "competition": random.choice(["Düşük", "Orta", "Yüksek"]),
                "monthly_searches": int(random.uniform(2000, 45000)),
                "ebay_url": f"https://www.ebay.com/sch/i.html?_nkw={dp.get('title', '').replace(' ', '+')}",
                "amazon_url": f"https://www.amazon.com/s?k={dp.get('title', '').replace(' ', '+')}",
                "aliexpress_url": f"https://www.aliexpress.com/wholesale?SearchText={dp.get('title', '').replace(' ', '+')}",
                "trendyol_url": f"https://www.trendyol.com/sr?q={dp.get('title', '').replace(' ', '+')}",
            }
            
            product = Product(**p_data)
            db.add(product)
            await db.flush()

            # Geçmiş 30 günün fiyat geçmişini simüle et
            base_price = p_data["market_price"]
            for days_ago in range(30, -1, -1):
                variation = random.uniform(-0.05, 0.08)
                hist_price = round(base_price * (1 + variation), 2)
                ph = PriceHistory(
                    product_id=product.id,
                    price=hist_price,
                    recorded_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.add(ph)

            # Geçmiş 7 günün trend istatistiklerini simüle et
            for days_ago in range(7, -1, -1):
                tp = TrendingProduct(
                    product_id=product.id,
                    trend_score=p_data["trend_score"] * random.uniform(0.85, 1.0),
                    category=p_data["category"],
                    date=today - timedelta(days=days_ago)
                )
                db.add(tp)

        await db.commit()
        print(f"Başarıyla {len(fake_products)} ürün sahte API'den çekilip veritabanına kaydedildi.")

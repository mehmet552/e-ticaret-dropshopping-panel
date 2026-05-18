import asyncio
import random
from datetime import datetime, timedelta, date
from models.database import AsyncSessionLocal, Product, PriceHistory, TrendingProduct


SEED_PRODUCTS = [
    {
        "name": "Kablosuz Bluetooth Kulaklık",
        "category": "Elektronik",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
        "supplier_price": 12.50,
        "market_price": 49.99,
        "trend_score": 94,
        "roi_percent": 299.9,
        "competition": "Düşük",
        "monthly_searches": 18500,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=wireless+bluetooth+earbuds",
        "amazon_url": "https://www.amazon.com/s?k=wireless+bluetooth+earbuds",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=wireless+earbuds",
        "trendyol_url": "https://www.trendyol.com/sr?q=bluetooth+kulakl%C4%B1k",
    },
    {
        "name": "LED Şerit Işık (5m)",
        "category": "Ev & Yaşam",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
        "supplier_price": 4.80,
        "market_price": 22.99,
        "trend_score": 88,
        "roi_percent": 379.0,
        "competition": "Orta",
        "monthly_searches": 24000,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=led+strip+lights+5m",
        "amazon_url": "https://www.amazon.com/s?k=led+strip+lights",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=led+strip+lights",
        "trendyol_url": "https://www.trendyol.com/sr?q=led+şerit+ışık",
    },
    {
        "name": "Masaj Tabancası Pro",
        "category": "Spor & Fitness",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&q=80",
        "supplier_price": 18.00,
        "market_price": 69.99,
        "trend_score": 91,
        "roi_percent": 288.8,
        "competition": "Düşük",
        "monthly_searches": 15200,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=massage+gun",
        "amazon_url": "https://www.amazon.com/s?k=massage+gun",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=massage+gun",
        "trendyol_url": "https://www.trendyol.com/sr?q=masaj+tabancası",
    },
    {
        "name": "Akıllı Saat Fitness Tracker",
        "category": "Elektronik",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
        "supplier_price": 22.00,
        "market_price": 79.99,
        "trend_score": 86,
        "roi_percent": 263.6,
        "competition": "Yüksek",
        "monthly_searches": 32000,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=smart+watch+fitness",
        "amazon_url": "https://www.amazon.com/s?k=fitness+smartwatch",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=smartwatch+fitness",
        "trendyol_url": "https://www.trendyol.com/sr?q=akıllı+saat",
    },
    {
        "name": "Aromaterapi Difüzör",
        "category": "Ev & Yaşam",
        "image_url": "https://images.unsplash.com/photo-1602928321679-560bb453f190?w=400&q=80",
        "supplier_price": 8.50,
        "market_price": 34.99,
        "trend_score": 79,
        "roi_percent": 311.6,
        "competition": "Orta",
        "monthly_searches": 11800,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=aromatherapy+diffuser",
        "amazon_url": "https://www.amazon.com/s?k=aromatherapy+diffuser",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=aroma+diffuser",
        "trendyol_url": "https://www.trendyol.com/sr?q=difüzör",
    },
    {
        "name": "Direnç Bantları Seti (5'li)",
        "category": "Spor & Fitness",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&q=80",
        "supplier_price": 3.20,
        "market_price": 19.99,
        "trend_score": 83,
        "roi_percent": 524.7,
        "competition": "Orta",
        "monthly_searches": 14500,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=resistance+bands+set",
        "amazon_url": "https://www.amazon.com/s?k=resistance+bands+set",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=resistance+bands",
        "trendyol_url": "https://www.trendyol.com/sr?q=direnç+bandı",
    },
    {
        "name": "Telefon Lens Seti (4'lü)",
        "category": "Elektronik",
        "image_url": "https://images.unsplash.com/photo-1495707902641-75cac588d2e9?w=400&q=80",
        "supplier_price": 5.50,
        "market_price": 24.99,
        "trend_score": 72,
        "roi_percent": 354.4,
        "competition": "Düşük",
        "monthly_searches": 8900,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=phone+camera+lens+kit",
        "amazon_url": "https://www.amazon.com/s?k=phone+lens+kit",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=phone+lens+kit",
        "trendyol_url": "https://www.trendyol.com/sr?q=telefon+lens",
    },
    {
        "name": "Taşınabilir Mini Projeksiyon",
        "category": "Elektronik",
        "image_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&q=80",
        "supplier_price": 35.00,
        "market_price": 119.99,
        "trend_score": 76,
        "roi_percent": 242.8,
        "competition": "Düşük",
        "monthly_searches": 7600,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=mini+portable+projector",
        "amazon_url": "https://www.amazon.com/s?k=mini+projector+portable",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=mini+projector",
        "trendyol_url": "https://www.trendyol.com/sr?q=mini+projeksiyon",
    },
    {
        "name": "Köpek GPS Takip Cihazı",
        "category": "Evcil Hayvan",
        "image_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&q=80",
        "supplier_price": 14.00,
        "market_price": 54.99,
        "trend_score": 85,
        "roi_percent": 292.8,
        "competition": "Düşük",
        "monthly_searches": 9800,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=dog+gps+tracker",
        "amazon_url": "https://www.amazon.com/s?k=dog+gps+tracker",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=pet+gps+tracker",
        "trendyol_url": "https://www.trendyol.com/sr?q=köpek+gps",
    },
    {
        "name": "Sera Bitkisi Büyüme Lambası",
        "category": "Ev & Yaşam",
        "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80",
        "supplier_price": 9.00,
        "market_price": 35.99,
        "trend_score": 81,
        "roi_percent": 299.9,
        "competition": "Düşük",
        "monthly_searches": 10200,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=plant+grow+light",
        "amazon_url": "https://www.amazon.com/s?k=grow+light+plant",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=plant+grow+light",
        "trendyol_url": "https://www.trendyol.com/sr?q=bitki+büyüme+lambası",
    },
    {
        "name": "Elektrikli Yüz Temizleme Fırçası",
        "category": "Güzellik",
        "image_url": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80",
        "supplier_price": 6.50,
        "market_price": 29.99,
        "trend_score": 78,
        "roi_percent": 361.4,
        "competition": "Orta",
        "monthly_searches": 12400,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=electric+facial+cleanser+brush",
        "amazon_url": "https://www.amazon.com/s?k=electric+face+cleansing+brush",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=facial+cleansing+brush",
        "trendyol_url": "https://www.trendyol.com/sr?q=yüz+temizleme+fırçası",
    },
    {
        "name": "Akıllı Su Şişesi (Isı Takipli)",
        "category": "Spor & Fitness",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&q=80",
        "supplier_price": 7.80,
        "market_price": 32.99,
        "trend_score": 74,
        "roi_percent": 323.0,
        "competition": "Düşük",
        "monthly_searches": 8100,
        "ebay_url": "https://www.ebay.com/sch/i.html?_nkw=smart+water+bottle+temperature",
        "amazon_url": "https://www.amazon.com/s?k=smart+water+bottle",
        "aliexpress_url": "https://www.aliexpress.com/wholesale?SearchText=smart+water+bottle",
        "trendyol_url": "https://www.trendyol.com/sr?q=akıllı+su+şişesi",
    },
]


async def seed_database():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(Product))
        count = result.scalar()
        if count and count > 0:
            return

        today = date.today()
        for i, p_data in enumerate(SEED_PRODUCTS):
            product = Product(**p_data)
            db.add(product)
            await db.flush()

            # Price history (last 30 days)
            base_price = p_data["market_price"]
            for days_ago in range(30, -1, -1):
                variation = random.uniform(-0.08, 0.05)
                hist_price = round(base_price * (1 + variation), 2)
                ph = PriceHistory(
                    product_id=product.id,
                    price=hist_price,
                    recorded_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.add(ph)

            # Trending records (last 7 days)
            for days_ago in range(7, -1, -1):
                tp = TrendingProduct(
                    product_id=product.id,
                    trend_score=p_data["trend_score"] * random.uniform(0.85, 1.0),
                    category=p_data["category"],
                    date=today - timedelta(days=days_ago)
                )
                db.add(tp)

        await db.commit()

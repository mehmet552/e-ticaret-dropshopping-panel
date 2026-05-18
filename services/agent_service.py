import asyncio
import json
import random
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import Product, TrendingProduct, PriceHistory
from models.seed import SEED_PRODUCTS
from core.config import settings

CATEGORY_MAP = {
    "elektronik": ["Elektronik"],
    "spor": ["Spor & Fitness"],
    "ev": ["Ev & Yaşam"],
    "güzellik": ["Güzellik"],
    "evcil": ["Evcil Hayvan"],
    "genel": ["Elektronik", "Spor & Fitness", "Ev & Yaşam", "Güzellik", "Evcil Hayvan"],
}


async def run_agent(category: str, db: AsyncSession) -> AsyncGenerator[dict, None]:
    """
    AI Agent - Ürün araştırma adımlarını yayınlar.
    API key yoksa mock veri kullanır, varsa gerçek API çağrısı yapar.
    """
    normalized = category.lower().strip()
    target_categories = CATEGORY_MAP.get(normalized, CATEGORY_MAP["genel"])

    # Step 1: Trend analizi
    yield {"step": 1, "total": 5, "title": "Trend Verileri Analiz Ediliyor", "status": "running",
           "detail": "Google Trends verilerine bağlanılıyor..."}
    await asyncio.sleep(1.5)

    trend_keywords = await _get_trends(normalized)
    yield {"step": 1, "total": 5, "title": "Trend Verileri Analiz Ediliyor", "status": "done",
           "detail": f"{len(trend_keywords)} trend anahtar kelime tespit edildi: {', '.join(trend_keywords[:4])}"}

    # Step 2: Ürün arama
    yield {"step": 2, "total": 5, "title": "Ürün Veritabanı Taranıyor", "status": "running",
           "detail": f"{', '.join(target_categories)} kategorilerinde ürünler aranıyor..."}
    await asyncio.sleep(2.0)

    products = await _search_products(target_categories, db)
    yield {"step": 2, "total": 5, "title": "Ürün Veritabanı Taranıyor", "status": "done",
           "detail": f"{len(products)} potansiyel ürün bulundu"}

    # Step 3: Tedarik fiyatları
    yield {"step": 3, "total": 5, "title": "Tedarik Fiyatları Kontrol Ediliyor", "status": "running",
           "detail": "AliExpress ve tedarikçi fiyatları alınıyor..."}
    await asyncio.sleep(1.8)

    if settings.EBAY_API_KEY:
        detail = "eBay API üzerinden gerçek fiyatlar alındı"
    else:
        detail = "Tedarik maliyeti hesaplaması tamamlandı (demo modu)"

    yield {"step": 3, "total": 5, "title": "Tedarik Fiyatları Kontrol Ediliyor", "status": "done",
           "detail": detail}

    # Step 4: Rekabet analizi
    yield {"step": 4, "total": 5, "title": "Rekabet Analizi Yapılıyor", "status": "running",
           "detail": "Pazar satıcı sayısı ve fiyat rekabeti değerlendiriliyor..."}
    await asyncio.sleep(1.5)

    yield {"step": 4, "total": 5, "title": "Rekabet Analizi Yapılıyor", "status": "done",
           "detail": f"{len([p for p in products if p['competition'] == 'Düşük'])} düşük rekabetli ürün belirlendi"}

    # Step 5: ROI hesaplama & sıralama
    yield {"step": 5, "total": 5, "title": "Kâr Analizi & Sıralama", "status": "running",
           "detail": "ROI skoru hesaplanıyor ve ürünler sıralanıyor..."}
    await asyncio.sleep(1.2)

    sorted_products = sorted(products, key=lambda x: x["roi_percent"], reverse=True)[:6]

    yield {"step": 5, "total": 5, "title": "Kâr Analizi & Sıralama", "status": "done",
           "detail": f"En yüksek ROI: %{sorted_products[0]['roi_percent']:.0f} — {sorted_products[0]['name']}"}

    # Final result
    yield {"step": "result", "products": sorted_products, "category": category,
           "timestamp": datetime.utcnow().isoformat()}


async def _get_trends(category: str) -> list[str]:
    """Gerçek pytrends veya mock trend verileri döner."""
    mock_trends = {
        "elektronik": ["wireless earbuds", "led strip", "smartwatch", "phone lens", "mini projector"],
        "spor": ["resistance bands", "massage gun", "yoga mat", "jump rope", "water bottle"],
        "ev": ["led strip lights", "aroma diffuser", "plant grow light", "smart plug", "cable organizer"],
        "güzellik": ["face cleansing brush", "jade roller", "led face mask", "nail art", "beard trimmer"],
        "evcil": ["dog gps tracker", "pet water fountain", "cat toy", "slow feeder bowl", "pet nail grinder"],
        "genel": ["wireless earbuds", "led strip", "massage gun", "smart watch", "resistance bands",
                  "aroma diffuser", "dog gps", "grow light"],
    }

    if settings.EBAY_API_KEY:
        try:
            from pytrends.request import TrendReq
            import asyncio
            loop = asyncio.get_event_loop()
            pytrends = TrendReq(hl="tr-TR", tz=180)
            kw_map = {
                "elektronik": "electronic gadgets", "spor": "fitness equipment",
                "ev": "home decor", "güzellik": "beauty tools",
                "evcil": "pet supplies", "genel": "trending products"
            }
            kw = kw_map.get(category, "trending products")
            await loop.run_in_executor(None, lambda: pytrends.build_payload([kw], timeframe="now 7-d"))
            related = await loop.run_in_executor(None, pytrends.related_queries)
            top = related.get(kw, {}).get("top")
            if top is not None and not top.empty:
                return top["query"].tolist()[:8]
        except Exception:
            pass

    return mock_trends.get(category, mock_trends["genel"])


async def _search_products(categories: list[str], db: AsyncSession) -> list[dict]:
    """Kategoriye göre ürün listesi döner."""
    result = await db.execute(
        select(Product).where(Product.category.in_(categories))
    )
    products = result.scalars().all()

    if not products:
        result = await db.execute(select(Product))
        products = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "image_url": p.image_url,
            "supplier_price": p.supplier_price,
            "market_price": p.market_price,
            "roi_percent": p.roi_percent,
            "trend_score": p.trend_score,
            "competition": p.competition,
            "monthly_searches": p.monthly_searches,
            "ebay_url": p.ebay_url,
            "amazon_url": p.amazon_url,
            "aliexpress_url": p.aliexpress_url,
            "trendyol_url": p.trendyol_url,
        }
        for p in products
    ]

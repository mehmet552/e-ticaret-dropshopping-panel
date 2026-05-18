from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.database import get_db, Product, TrendingProduct, PriceHistory

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/trending")
async def get_trending(
    category: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).order_by(desc(Product.trend_score)).limit(limit)
    if category:
        query = select(Product).where(Product.category == category).order_by(desc(Product.trend_score)).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return [_product_to_dict(p) for p in products]


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product.category).distinct())
    categories = [row[0] for row in result.fetchall()]
    return categories


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return _product_to_dict(product)


@router.get("/{product_id}/history")
async def get_price_history(product_id: int, days: int = Query(30, le=90), db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id, PriceHistory.recorded_at >= since)
        .order_by(PriceHistory.recorded_at)
    )
    history = result.scalars().all()
    return [{"price": h.price, "date": h.recorded_at.isoformat()} for h in history]


def _product_to_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "image_url": p.image_url,
        "supplier_price": p.supplier_price,
        "market_price": p.market_price,
        "currency": p.currency,
        "trend_score": p.trend_score,
        "roi_percent": p.roi_percent,
        "competition": p.competition,
        "monthly_searches": p.monthly_searches,
        "ebay_url": p.ebay_url,
        "amazon_url": p.amazon_url,
        "aliexpress_url": p.aliexpress_url,
        "trendyol_url": p.trendyol_url,
        "last_updated": p.last_updated.isoformat() if p.last_updated else None,
    }

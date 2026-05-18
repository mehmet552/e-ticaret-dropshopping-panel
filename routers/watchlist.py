from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.database import get_db, Watchlist, Product, User
from core.security import get_current_user

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAdd(BaseModel):
    product_id: int
    target_price: Optional[float] = None


@router.get("")
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(Watchlist.user_id == current_user.id)
    )
    items = result.scalars().all()

    response = []
    for item in items:
        prod = await db.execute(select(Product).where(Product.id == item.product_id))
        product = prod.scalar_one_or_none()
        if product:
            response.append({
                "id": item.id,
                "product_id": item.product_id,
                "target_price": item.target_price,
                "added_at": item.added_at.isoformat(),
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "image_url": product.image_url,
                    "market_price": product.market_price,
                    "supplier_price": product.supplier_price,
                    "roi_percent": product.roi_percent,
                    "trend_score": product.trend_score,
                    "ebay_url": product.ebay_url,
                    "amazon_url": product.amazon_url,
                    "aliexpress_url": product.aliexpress_url,
                    "trendyol_url": product.trendyol_url,
                }
            })
    return response


@router.post("")
async def add_to_watchlist(
    body: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Zaten var mı?
    existing = await db.execute(
        select(Watchlist).where(
            Watchlist.user_id == current_user.id,
            Watchlist.product_id == body.product_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ürün zaten takip listesinde")

    item = Watchlist(
        user_id=current_user.id,
        product_id=body.product_id,
        target_price=body.target_price,
    )
    db.add(item)
    await db.flush()
    return {"id": item.id, "message": "Takip listesine eklendi"}


@router.delete("/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(Watchlist.id == item_id, Watchlist.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    await db.delete(item)
    return {"message": "Takip listesinden çıkarıldı"}


@router.patch("/{item_id}/target")
async def update_target_price(
    item_id: int,
    target_price: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(Watchlist.id == item_id, Watchlist.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    item.target_price = target_price
    return {"message": "Hedef fiyat güncellendi"}

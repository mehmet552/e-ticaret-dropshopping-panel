from datetime import datetime
from typing import AsyncGenerator, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Date, Text
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String)
    supplier_price = Column(Float)
    market_price = Column(Float)
    currency = Column(String, default="USD")
    trend_score = Column(Integer, default=0)
    roi_percent = Column(Float, default=0)
    competition = Column(String, default="Orta")
    monthly_searches = Column(Integer, default=0)
    ebay_url = Column(String)
    amazon_url = Column(String)
    aliexpress_url = Column(String)
    trendyol_url = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete")
    trending = relationship("TrendingProduct", back_populates="product", cascade="all, delete")
    watchlist = relationship("Watchlist", back_populates="product", cascade="all, delete")
    notifications = relationship("Notification", back_populates="product", cascade="all, delete")


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    price = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="price_history")


class TrendingProduct(Base):
    __tablename__ = "trending_products"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    trend_score = Column(Float)
    category = Column(String)
    date = Column(Date, default=datetime.utcnow)
    product = relationship("Product", back_populates="trending")


class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    target_price = Column(Float, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="watchlist")
    product = relationship("Product", back_populates="watchlist")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications")
    product = relationship("Product", back_populates="notifications")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sqlalchemy import select
from models.database import AsyncSessionLocal, Watchlist, Product, Notification
from core.config import settings


async def check_price_drops():
    """Tüm watchlist ürünlerini kontrol eder, fiyat düşüşü varsa bildirim oluşturur."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Watchlist).where(Watchlist.target_price.isnot(None))
        )
        items = result.scalars().all()

        for item in items:
            prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
            product = prod_result.scalar_one_or_none()
            if not product:
                continue

            if product.market_price <= item.target_price:
                # Bildirim var mı kontrol et (aynı gün tekrar gönderme)
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                existing = await db.execute(
                    select(Notification).where(
                        Notification.user_id == item.user_id,
                        Notification.product_id == item.product_id,
                        Notification.created_at >= today_start
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Bildirim oluştur
                notification = Notification(
                    user_id=item.user_id,
                    product_id=item.product_id,
                    message=f'"{product.name}" ürününün fiyatı ${product.market_price:.2f} seviyesine düştü! '
                            f'Hedef fiyatınız: ${item.target_price:.2f}',
                )
                db.add(notification)

                # E-posta gönder
                await _send_price_drop_email(item.user_id, product, item.target_price, db)

        await db.commit()


async def _send_price_drop_email(user_id: int, product, target_price: float, db):
    """Fiyat düşüşü e-posta bildirimi gönderir."""
    from models.database import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"💰 Fiyat Düştü: {product.name}"
        msg["From"] = "noreply@dropagent.com"
        msg["To"] = user.email

        html = f"""
        <html><body style="font-family: Inter, sans-serif; background: #f9fafb; padding: 32px;">
          <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; padding: 32px; border: 1px solid #e5e7eb;">
            <h2 style="color: #111827; margin: 0 0 8px 0;">💰 Fiyat Düştü!</h2>
            <p style="color: #6b7280; margin: 0 0 24px 0;">Takip ettiğiniz ürün hedef fiyata ulaştı.</p>
            <div style="background: #f9fafb; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
              <p style="margin: 0; font-weight: 600; color: #111827;">{product.name}</p>
              <p style="margin: 8px 0 0 0; color: #2563eb; font-size: 24px; font-weight: 700;">${product.market_price:.2f}</p>
              <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">Hedef fiyatınız: ${target_price:.2f}</p>
            </div>
            <a href="{product.ebay_url}" style="background: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block;">eBay'de Gör →</a>
          </div>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail("noreply@dropagent.com", user.email, msg.as_string())
    except Exception as e:
        print(f"E-posta gönderilemedi: {e}")

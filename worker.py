from celery import Celery
from celery.schedules import crontab
from core.config import settings
import asyncio

celery_app = Celery(
    "dropagent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Istanbul",
    enable_utc=True,
    beat_schedule={
        "check-price-drops-every-6-hours": {
            "task": "worker.task_check_prices",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)


@celery_app.task(name="worker.task_check_prices")
def task_check_prices():
    """Her 6 saatte fiyat düşüşlerini kontrol eder."""
    from services.price_monitor import check_price_drops
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(check_price_drops())
    finally:
        loop.close()

import json
import re
from typing import Any

import httpx

from core.config import settings


async def query_groq(prompt: str, max_tokens: int = 150) -> str:
    """Groq API üzerinden bir tamamlayıcı isteği gönderir."""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ API anahtarı ayarlı değil.")

    url = f"{settings.GROQ_API_URL}/completions"
    payload = {
        "model": settings.GROQ_MODEL,
        "input": prompt,
        "max_output_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return _extract_text_from_groq_response(response.json())


def _extract_text_from_groq_response(data: Any) -> str:
    if isinstance(data, dict):
        if "output_text" in data and isinstance(data["output_text"], str):
            return data["output_text"]
        output = data.get("output")
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, list):
                return "".join(str(item) for item in first if item is not None)
            if isinstance(first, str):
                return first
        return json.dumps(data, ensure_ascii=False)
    return str(data)


async def get_groq_trends(category: str) -> list[str]:
    """Kategoriye göre Groq üzerinden trend anahtar kelimeleri döner."""
    prompt = (
        f"Dropshipping için '{category}' kategorisinde şu anda yüksek talep gören ve "
        "yüksek kar potansiyeline sahip 5 ürün anahtar kelimesini Türkçe olarak virgülle ayrılmış şekilde yaz."
    )
    raw_text = await query_groq(prompt, max_tokens=120)
    items = [item.strip().strip(".-") for item in re.split(r"[\n,]+", raw_text) if item.strip()]
    return items[:5]

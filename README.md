# DropAgent 🤖

AI destekli dropshipping ürün araştırma platformu.

## Kurulum

```bash
git clone <repo>
cd dropagent
cp .env.example .env
docker-compose up --build
```

Açık adresler:
- **Uygulama:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **MailHog (e-posta):** http://localhost:8025

## API Key Ekleme

`.env` dosyasını düzenle:
```
EBAY_API_KEY=senin_key_burada
RAPIDAPI_KEY=senin_key_burada
```
Sonra `docker-compose restart backend worker` komutunu çalıştır.

## Özellikler

- 🤖 AI Agent: Gerçek zamanlı ürün araştırma
- 📈 Trend Ürünler: Tarihsel veri ile kategori bazlı listeleme
- 👤 Kullanıcı Hesapları: JWT tabanlı kimlik doğrulama
- 📋 Takip Listesi: Ürün fiyat takibi
- 🔔 Bildirimler: Fiyat düşüşünde otomatik uyarı

# DropAgent 

AI destekli dropshipping ürün araştırma platformu.

## Kurulum

```bash
git clone <repo>
cd dropagent
cp .env.example .env
docker-compose up --build
```



## Sahte API ile Çalışma

Bu proje sahte/demo veriler üzerine kurulmuştur. Temel çalışma şekli yerel mock veriler ve DummyJSON sahte ürün kaynağı üzerinden ilerler.

Projeyi çalıştırmak için ek `.env` ayarı yapmanız şart değil. Mevcut durumda tüm trend ve ürün verisi yerelde mock/sahte kaynaklardan sağlanır.

## Groq API Entegrasyonu

Bu proje Groq API anahtarı ile AI Agent için canlı trend verisi alabilir. `services/groq_service.py` üzerinden Groq `completions` endpoint'ine istekte bulunulur.

`.env` dosyanıza aşağıdaki satırları ekleyin:

```env
GROQ_API_URL=https://api.groq.ai/v1
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=groq-1
```

- `GROQ_API_URL` varsayılan olarak `https://api.groq.ai/v1` olarak ayarlanmıştır.
- `GROQ_MODEL` ise `groq-1` varsayımıyla çalışır.

Eğer `GROQ_API_KEY` yoksa veya Groq isteği başarısız olursa, sistem otomatik olarak demo/mock trend verisine döner.

## Özellikler

-  AI Agent: Gerçek zamanlı ürün araştırma
-  Trend Ürünler: Tarihsel veri ile kategori bazlı listeleme
-  Kullanıcı Hesapları: JWT tabanlı kimlik doğrulama
-  Takip Listesi: Ürün fiyat takibi
-  Bildirimler: Fiyat düşüşünde otomatik uyarı

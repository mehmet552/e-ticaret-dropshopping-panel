# DropAgent

AI destekli dropshipping ürün araştırma platformu.

## Hızlı Başlangıç

1. Depoyu klonlayın:

```powershell
git clone <repo>
cd dropagent
```

2. Ortam dosyası oluşturun:

```powershell
copy .env.example .env
```

3. Uygulamayı başlatın:

```powershell
.\start.ps1
```

Alternatif olarak:

```powershell
python main.py
```

## Nasıl Çalışır

- `main.py` FastAPI backend ve `static/` içindeki frontend dosyalarını sunar.
- `start.ps1` Python bağımlılıklarını (`requirements-local.txt`) yükler ve uygulamayı başlatır.
- Statik varlıklar `/assets` altında sunulur.

## Kullanıcı Deneyimi

- Uygulama ilk açıldığında bir karşılama/giriş sayfası gösterilir.
- Kullanıcı giriş yapana veya kayıt olana kadar dashboard içeriği gizlidir.
- Giriş yaptıktan sonra ana menü bir sidebar olarak sunulur.
- Aydınlık/karanlık tema seçimi geçerlidir ve tüm uygulama bileşenlerini kapsayacak şekilde çalışır.

## Sahte API / Demo Veri

Bu proje sahte/demo veriler üzerine kuruludur. Ürünler, takip listesi ve trend sayfaları yerel mock veriler ile çalışır.

- Projeyi çalıştırmak için Groq API anahtarı zorunlu değildir.
- Canlı veri yoksa sistem demo/mock moda geçer.

## Groq API Entegrasyonu (Opsiyonel)

AI Agent için canlı trend verisi almak isterseniz `.env` dosyasına aşağıdaki değerleri ekleyin:

```env
GROQ_API_URL=https://api.groq.ai/v1
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=groq-1
```

- `GROQ_API_URL` varsayılan olarak `https://api.groq.ai/v1` olarak ayarlanmıştır.
- `GROQ_MODEL` varsayılan değeri `groq-1`'dir.
- Eğer `GROQ_API_KEY` yoksa veya Groq isteği başarısız olursa sistem otomatik olarak demo/mocks veriye döner.

## Öne Çıkan Özellikler

- AI destekli ürün araştırması
- Kategori bazlı trend ürünler
- JWT tabanlı kullanıcı girişi ve kayıt
- Takip listesi ile hedef fiyat takibi
- Bildirimler ve okunmamış sayacı
- Karanlık / aydınlık tema desteği
- Landing page + auth-first kullanıcı akışı

## Notlar

- `görseller/` klasöründeki görüntüler `static/images/` içine kopyalanarak frontend tarafından sunulur.
- `dropagent.db` proje veritabanını içerir. Çalıştırmadan önce dosyayı silip yeniden başlatırsanız veritabanı yeniden oluşturulur.
- API belgeleri `http://localhost:8000/docs` adresinden erişilebilir.

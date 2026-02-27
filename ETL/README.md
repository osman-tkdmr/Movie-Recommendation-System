# Dağıtık IMDb Veri Çekme Sistemi

Bu proje, IMDb ID'lerini kullanarak The Movie Database (TMDb) API'sinden film ve dizi verilerini çekmek için dağıtık bir sistem sağlar. Sistem, 16 farklı kullanıcı arasında iş yükünü paylaştırarak veri çekme işlemini hızlandırır.

## Sistem Yapısı

- **Modüler Yapı**: Tüm veri çekme işlemleri tek bir modüler `find_content_imdb_id.py` dosyası ile gerçekleştirilir.
- **Merkezi Konfigürasyon**: API anahtarları ve kullanıcı dağılımı `central_config.py` dosyasında merkezi olarak yönetilir.
- **Tek Sanal Ortam**: Tüm sistem için tek bir sanal ortam kullanılır.

## Kurulum

1. Sanal ortamı oluşturun ve etkinleştirin:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

## Kullanım

### Veri Çekme İşlemi

Belirli bir kullanıcı ID'si için veri çekme işlemini başlatmak için:

```bash
python run_scraper.py <user_id>
```

Burada `<user_id>` 0 ile 15 arasında bir değer olmalıdır.

Tüm kullanıcılar için sırayla veri çekme işlemini başlatmak için:

```bash
python run_scraper.py all
```

### Veri Dönüştürme ve Yükleme

Çekilen verileri dönüştürmek için:

```bash
python transform_imdb_json.py
```

Dönüştürülen verileri veritabanına yüklemek için:

```bash
python transferData2db.py
```

## Dosya Yapısı

- `find_content_imdb_id.py`: Modüler veri çekme sınıfı ve işlemleri
- `central_config.py`: Merkezi konfigürasyon ve API anahtarları
- `run_scraper.py`: Veri çekme işlemini başlatma betiği
- `transform_imdb_json.py`: Çekilen verileri dönüştürme betiği
- `transferData2db.py`: Dönüştürülen verileri veritabanına yükleme betiği
- `requirements.txt`: Gerekli Python paketleri
- `Moppie0-15/`: Her kullanıcı için ayrı veri klasörleri

## Veri Akışı

1. IMDb ID'leri `imdb_ids_cache.json` dosyasından yüklenir
2. Her kullanıcıya belirli bir ID aralığı atanır
3. Her ID için TMDb API'sine istek yapılır
4. Sonuçlar `data.json` dosyalarına kaydedilir
5. Veriler `transform_imdb_json.py` ile dönüştürülür
6. Dönüştürülen veriler `transferData2db.py` ile veritabanına yüklenir

## Hata Yönetimi

- Başarısız istekler `error_ids.json` dosyasına kaydedilir
- İlerleme durumu `progress.json` dosyasında takip edilir
- Sistem, önceki çalışmadan kaldığı yerden devam edebilir
- Başarısız istekler otomatik olarak yeniden denenir
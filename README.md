Hisse Senedi Tahmin ve Portföy Yönetim Uygulaması

Bu proje, yatırımcıların hisse senedi piyasasında daha bilinçli kararlar alabilmelerini sağlamak amacıyla geliştirilmiş bir tahmin ve portföy yönetim sistemidir. Kullanıcılar, hisse senetleri için fiyat tahminleri alabilir, teknik analiz göstergelerini inceleyebilir ve kendi portföylerini kolayca yönetebilirler.

Özellikler

Kullanıcı Yönetimi: Kullanıcılar kayıt olabilir ve sisteme giriş yapabilir.
Hisse Senedi Tahminleri: Makine öğrenimi algoritmalarıyla hisse senetleri için gelecek fiyat tahminleri.
Teknik Analiz: MA20, MA50, RSI gibi teknik göstergelerle detaylı analiz.
Portföy Yönetimi: Hisse senetlerini portföye ekleme, alış fiyatı ve miktarını belirterek performans takibi.
Grafiksel Gösterim: Hisse fiyatları ve teknik göstergelerin interaktif görsel sunumu.
Kurulum

Gerekli Yazılımlar
Proje için aşağıdaki yazılımların ve kütüphanelerin kurulu olması gerekmektedir:

Python (3.9 veya üzeri)
Flask Framework
SQLite
yfinance
scikit-learn
pandas
numpy
Adımlar
Proje Dosyalarını İndirin
git clone https://github.com/yourusername/hisse-tahmin-uygulamasi.git
cd hisse-tahmin-uygulamasi
Gerekli Python Kütüphanelerini Yükleyin
pip install -r requirements.txt
Veritabanını Hazırlayın
Veritabanı yapısını oluşturmak için ilgili script'i çalıştırın:
python setup_database.py
Uygulamayı Çalıştırın
Uygulamayı başlatmak için aşağıdaki komutu çalıştırın:
python app.py
Uygulama, tarayıcınızda http://127.0.0.1:5000 adresinde çalışacaktır.
Kullanım

Kayıt ve Giriş
Ana sayfadan kayıt olun veya mevcut bilgilerinizle giriş yapın.
Hisse Senedi Tahmini
Hisse kodunu girin (örn: THYAO.IS)
Tahmin tarihini seçin.
"Tahmin Et" butonuna tıklayın.
Portföy Yönetimi
"Portföy" sekmesinden hisse senedi ekleyin.
Alış fiyatı ve miktarını girerek portföyünüzü oluşturun.
Portföy performansınızı kolayca takip edin.
Teknik Detaylar

Veritabanı Yapısı
users Tablosu

Alan Tür Açıklama
id INTEGER Primary Key
username TEXT Kullanıcı Adı
password TEXT Şifre
portfolios Tablosu

Alan Tür Açıklama
id INTEGER Primary Key
user_id INTEGER Foreign Key (users.id)
symbol TEXT Hisse Sembolü
quantity INTEGER Miktar
purchase_price REAL Alış Fiyatı
purchase_date DATE Alış Tarihi
Kullanılan Teknolojiler
Backend: Flask (Python)
Frontend: HTML, CSS, JavaScript
Veritabanı: SQLite
Veri Kaynağı: Yahoo Finance API
Makine Öğrenimi: RandomForestRegressor
Önemli Dosyalar

app.py → Uygulamanın ana dosyası.
setup_database.py → Veritabanı kurulum script'i.
static/ → CSS ve JavaScript dosyaları.
templates/ → HTML dosyaları.
requirements.txt → Gerekli Python kütüphaneleri.
Katkıda Bulunma

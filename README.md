# Fergani Uydu Takip Platformu

Turk uydularini web arayuzu uzerinden takip etmeye yarayan FastAPI tabanli yerel uygulama.

## Kurulum

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

## Calistirma

```powershell
.\start_server.bat
```

Varsayilan yerel adres:

- `http://127.0.0.1:8000/ui`

## Ayni agdan erisim

Servisi sadece bilincli olarak agdan erisilebilir yapmak icin:

```powershell
.\share_lan.bat
```

Sonra ayni agdaki diger cihazlardan su adres acilir:

```text
http://BILGISAYAR_IP_ADRESI:8000/ui
```

Internet uzerinden erisim icin modem/router tarafinda secilen porta yonlendirme yapilmali veya Cloudflare Tunnel, Tailscale ya da ngrok gibi bir tunel servisi kullanilmalidir.

Guvenlik notu: Portu internete acmadan once sadece ihtiyac duyulan portu acin ve uygulamayi mumkunse bir tunel/VPN arkasindan yayinlayin.

## Istediginde baskalarina kullandirma

Normal kullanimda sadece `start_server.bat` calistirin; bu mod bilgisayarin disina acilmaz.

Ayni Wi-Fi veya yerel agdaki kisilere kullandirmak icin:

```powershell
.\share_lan.bat
```

Internet uzerinden gecici link vermek icin Cloudflare Tunnel kuruluysa:

```powershell
.\share_internet_cloudflare.bat
```

Bu komut ekranda gecici bir `https://...trycloudflare.com` linki verir. Bu linki paylasabilir veya QR koda cevirebilirsiniz. Bilgisayar kapaninca, internet kesilince veya komut penceresi kapaninca canli takip de durur.

Tek komutla GitHub Pages + canli API paylasim linki uretmek icin:

```powershell
.\start_public.bat
```

Bu komut `api_server.py --public` calistirir. API zaten `127.0.0.1:8000` uzerinde aciksa onu kullanir; acik degilse API'yi baslatir. Ekranda `PAYLASILACAK GITHUB LINKI` satiri gorundugunde o adresi QR koda cevirebilirsiniz.

Sabit QR kullanimi:

```text
https://klovoksilo-svg.github.io/fergani/
```

`start_public.bat` her calistiginda yeni Cloudflare adresini `data/current_api.json` dosyasina yazar ve GitHub'a gonderir. Bu nedenle QR sabit kalabilir; yalniz GitHub Pages'in yeni adresi yayinlamasi icin kisa bir sure beklemek gerekebilir.

PyCharm'da `api_server.py` dosyasini normal calistirirken de otomatik public mod acilsin istersen proje klasorunde `.fergani-public` adli bos bir dosya olusturun. Bu dosya GitHub'a gonderilmez; sadece bu bilgisayarda public modu varsayilan yapar.

## GitHub Pages + QR ile canli kullanim

GitHub Pages sadece arayuzu barindirir. Canli uydu verisi bu bilgisayardaki FastAPI servisinden gelir. Bu nedenle QR linki her zaman GitHub Pages adresini acabilir, fakat canli takip sadece bilgisayar acik, internet bagli ve API/tunel calisirken kullanilabilir.

1. GitHub reposunda Pages kaynagini `main` branch ve `/root` olarak ayarlayin.
2. Bilgisayarda API'yi agdan erisilebilir calistirin:

```powershell
$env:FERGANI_HOST = "0.0.0.0"
$env:FERGANI_PORT = "8000"
.\start_server.bat
```

3. Internetten erisim icin bir HTTPS tunel acin. Ornek tunel adresi:

```text
https://ornek-tunel-adresi.example
```

4. QR kodu su GitHub Pages linkinden uretin:

```text
https://ceyhu.github.io/fergani/?api=https%3A%2F%2Fornek-tunel-adresi.example
```

`api` parametresi ilk acilista tarayiciya kaydedilir. Tunel adresi degisirse QR linkindeki `api` degeri de guncellenmelidir.

GitHub Pages adresiniz farkliysa backend CORS listesine o adresi ekleyin:

```powershell
$env:FERGANI_CORS_ORIGINS = "https://ceyhu.github.io,http://127.0.0.1:8000,http://localhost:8000"
.\start_server.bat
```

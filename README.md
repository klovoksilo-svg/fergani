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
$env:FERGANI_HOST = "0.0.0.0"
$env:FERGANI_PORT = "8000"
.\start_server.bat
```

Sonra ayni agdaki diger cihazlardan su adres acilir:

```text
http://BILGISAYAR_IP_ADRESI:8000/ui
```

Internet uzerinden erisim icin modem/router tarafinda secilen porta yonlendirme yapilmali veya Cloudflare Tunnel, Tailscale ya da ngrok gibi bir tunel servisi kullanilmalidir.

Guvenlik notu: Portu internete acmadan once sadece ihtiyac duyulan portu acin ve uygulamayi mumkunse bir tunel/VPN arkasindan yayinlayin.

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

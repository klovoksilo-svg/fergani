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

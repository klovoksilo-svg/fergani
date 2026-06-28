@echo off
setlocal

cd /d "%~dp0"

where cloudflared >nul 2>nul
if errorlevel 1 (
    echo.
    echo Cloudflare Tunnel araci bulunamadi: cloudflared
    echo.
    echo Internetten gecici link vermek icin once cloudflared kurulmali.
    echo Kurduktan sonra bu dosyayi tekrar calistirin.
    echo.
    pause
    exit /b 1
)

set FERGANI_HOST=127.0.0.1
if "%FERGANI_PORT%"=="" set FERGANI_PORT=8000
set FERGANI_RELOAD=false

echo.
echo Fergani API ayri pencerede baslatiliyor.
echo Cloudflare birazdan gecici bir https linki verecek.
echo O linki veya linkten uretilen QR kodu paylasabilirsiniz.
echo Bilgisayar kapanirsa veya bu pencereler kapanirsa paylasim biter.
echo.

start "Fergani API" cmd /k ".venv\Scripts\python.exe api_server.py"
timeout /t 3 >nul
cloudflared tunnel --url http://127.0.0.1:%FERGANI_PORT%

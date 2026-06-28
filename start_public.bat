@echo off
setlocal

cd /d "%~dp0"

if "%FERGANI_PORT%"=="" set FERGANI_PORT=8000

echo.
echo Fergani genel paylasim modu baslatiliyor.
echo API ve Cloudflare Tunnel ayni pencerede acilacak.
echo Ekranda PAYLASILACAK GITHUB LINKI yazinca onu QR koda cevirebilirsiniz.
echo.

".venv\Scripts\python.exe" api_server.py --public

@echo off
setlocal

cd /d "%~dp0"

set FERGANI_HOST=0.0.0.0
if "%FERGANI_PORT%"=="" set FERGANI_PORT=8000
set FERGANI_RELOAD=false

echo.
echo Fergani ayni ag paylasim modu basliyor.
echo.
echo Bu bilgisayarin ag adresleri:
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -ne '127.0.0.1' } | ForEach-Object { '  http://' + $_.IPAddress + ':%FERGANI_PORT%/ui' }"
echo.
echo Ayni Wi-Fi veya yerel agdaki kisiler yukaridaki adreslerden birini acabilir.
echo Paylasimi kapatmak icin bu pencereyi kapatin veya Ctrl+C kullanin.
echo.

".venv\Scripts\python.exe" api_server.py

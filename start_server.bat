@echo off
setlocal

cd /d "%~dp0"

if "%FERGANI_HOST%"=="" set FERGANI_HOST=127.0.0.1
if "%FERGANI_PORT%"=="" set FERGANI_PORT=8000
if "%FERGANI_RELOAD%"=="" set FERGANI_RELOAD=false

".venv\Scripts\python.exe" api_server.py

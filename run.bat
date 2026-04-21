@echo off
cd /d "%~dp0"

echo Iniciando Web Scraper...
echo Abre tu navegador en: http://localhost:5001
echo Presiona Ctrl+C para detener.
echo.

start "" "http://localhost:5001"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe app.py
) else (
    python app.py
)

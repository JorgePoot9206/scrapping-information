#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "Iniciando Web Scraper..."
echo "Abre tu navegador en: http://localhost:5001"
echo "Presiona Ctrl+C para detener."
echo ""

# Abrir navegador según el sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:5001" 2>/dev/null &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:5001" 2>/dev/null &
fi

# Activar venv si existe, si no usar python del sistema
if [ -d "venv" ]; then
    ./venv/bin/python app.py
else
    python3 app.py
fi

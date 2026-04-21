FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Playwright/Chromium
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium para Playwright
RUN playwright install chromium

# Copiar el proyecto
COPY . .

# Puerto que Railway asigna dinámicamente
ENV PORT=8000

EXPOSE 8000

CMD gunicorn app:app \
    --workers 2 \
    --timeout 120 \
    --bind 0.0.0.0:$PORT \
    --log-level info

# Web Scraper

Una herramienta web para extraer información de cualquier sitio público: contenido, enlaces, imágenes, tablas y fuentes tipográficas.

## Características

- Extrae título, meta descripción, contenido textual, enlaces, imágenes, tablas y fuentes
- Fallback automático a Playwright (Chromium) para sitios renderizados con JavaScript
- Caché en memoria de 5 minutos para evitar peticiones repetidas
- Rate limiting: 3 solicitudes/minuto y 15/hora por IP
- Interfaz web limpia con pestañas para cada tipo de dato
- Compatible con Docker para despliegue fácil

## Requisitos

- Python 3.11 o superior
- pip

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/JorgePoot9206/scrapping-information.git
cd scrapping-information

# 2. Crea y activa el entorno virtual
python3 -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Instala el navegador para Playwright
playwright install chromium
```

## Uso

### Mac / Linux

```bash
bash run.sh
```

### Windows

```bat
run.bat
```

### Manual (cualquier sistema)

```bash
python app.py
```

Luego abre `http://localhost:5001` en tu navegador.

## Docker

```bash
# Construir la imagen
docker build -t web-scraper .

# Ejecutar el contenedor
docker run -p 8000:8000 web-scraper
```

Luego abre `http://localhost:8000`.

## Estructura del proyecto

```
├── app.py            # Servidor Flask y rutas
├── scraper.py        # Lógica de extracción (requests + Playwright)
├── templates/
│   └── index.html    # Interfaz web
├── requirements.txt
├── Dockerfile
├── run.sh            # Lanzador para Mac/Linux
└── run.bat           # Lanzador para Windows
```

## Licencia

MIT

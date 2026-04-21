import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import time

# Cache: { url -> (timestamp, result) }
_cache: dict = {}
CACHE_TTL = 300  # segundos (5 minutos)


def _get_cached(url: str):
    entry = _cache.get(url)
    if entry and (time.time() - entry[0]) < CACHE_TTL:
        return entry[1]
    return None


def _set_cache(url: str, result: dict):
    _cache[url] = (time.time(), result)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}


_CONTENT_TAGS = {"h1","h2","h3","h4","h5","h6","p","li","blockquote","strong","em","b","figcaption","dt","dd","caption"}
_SYSTEM_FONTS = {"inherit","initial","unset","revert","sans-serif","serif","monospace","cursive","fantasy","system-ui","ui-sans-serif","ui-serif","ui-monospace","-apple-system","blinkmacsystemfont"}


def _parse_html(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(strip=True) if soup.title else ""

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    if meta_tag:
        meta_desc = meta_tag.get("content", "")

    # ── Fuentes (antes de eliminar <style>) ──────────────────────
    fonts: set[str] = set()

    # Google Fonts / Typekit links
    for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in (r if isinstance(r, list) else [r])):
        href = link.get("href", "")
        if "fonts.googleapis.com" in href or "use.typekit.net" in href:
            for m in re.findall(r'family=([^&|+:@]+)', href):
                name = m.replace("+", " ").strip()
                if name:
                    fonts.add(name)

    # @font-face y font-family en bloques <style>
    for style_tag in soup.find_all("style"):
        css = style_tag.get_text()
        for m in re.findall(r'font-family\s*:\s*["\']?([^;"\']+)["\']?', css, re.I):
            name = m.strip().strip("\"'").split(",")[0].strip()
            if name and len(name) < 60 and name.lower() not in _SYSTEM_FONTS:
                fonts.add(name)

    # font-family en atributos style inline
    for el in soup.find_all(style=True):
        for m in re.findall(r'font-family\s*:\s*["\']?([^;"\']+)["\']?', el["style"], re.I):
            name = m.strip().strip("\"'").split(",")[0].strip()
            if name and len(name) < 60 and name.lower() not in _SYSTEM_FONTS:
                fonts.add(name)

    # Remove noise tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # ── Contenido en orden del documento ─────────────────────────
    # Solo incluye un elemento si ningún ancestro suyo es también un tag de contenido
    # (evita duplicados por anidamiento: <p><strong>x</strong></p> → solo <p>)
    content = []
    for el in soup.find_all(_CONTENT_TAGS):
        if any(parent.name in _CONTENT_TAGS for parent in el.parents):
            continue
        text = el.get_text(strip=True)
        if not text:
            continue
        if el.name in ("p", "dd", "dt") and len(text) <= 40:
            continue
        content.append({"tag": el.name, "text": text})

    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)
        if href.startswith("http") and href not in seen:
            seen.add(href)
            links.append({"text": text or href, "url": href})

    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        alt = img.get("alt", "").strip()
        if src and src.startswith("http"):
            images.append({"src": src, "alt": alt})

    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(rows)

    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "fonts": sorted(fonts),
        "content": content[:80],
        "links": links[:50],
        "images": images[:20],
        "tables": tables[:5],
        "method": "requests",
    }


def scrape_with_requests(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return _parse_html(resp.text, url)


def scrape_with_playwright(url: str) -> dict:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=HEADERS["User-Agent"],
            locale="es-MX",
        )
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()

    result = _parse_html(html, url)
    result["method"] = "playwright"
    return result


def scrape(url: str) -> dict:
    """
    Tries requests first; falls back to Playwright if the page
    appears to be JavaScript-rendered (too little content).
    Resultados se cachean por CACHE_TTL segundos para no repetir llamadas.
    """
    cached = _get_cached(url)
    if cached:
        return {**cached, "cached": True}

    try:
        result = scrape_with_requests(url)
        if len(result["content"]) < 3:
            result = scrape_with_playwright(url)
        _set_cache(url, result)
        return result
    except Exception as req_err:
        try:
            result = scrape_with_playwright(url)
            _set_cache(url, result)
            return result
        except Exception as pw_err:
            return {"error": f"requests: {req_err} | playwright: {pw_err}", "url": url}

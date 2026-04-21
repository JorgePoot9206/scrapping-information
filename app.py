import os
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scraper import scrape

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
@limiter.limit("3 per minute")
@limiter.limit("15 per hour")
def do_scrape():
    data = request.get_json()
    url = (data or {}).get("url", "").strip()

    if not url:
        return jsonify({"error": "Por favor ingresa una URL válida."}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = scrape(url)
    return jsonify(result)


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        "error": f"Demasiadas solicitudes. {e.description}"
    }), 429


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, port=port)

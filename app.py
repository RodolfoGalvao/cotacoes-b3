from flask import Flask, render_template, jsonify
from services.stock_service import fetch_all_quotes, fetch_history
from config import REFRESH_INTERVAL_SECONDS

app = Flask(__name__)


@app.route("/")
def index():
    quotes = fetch_all_quotes()
    return render_template(
        "index.html",
        quotes=quotes,
        refresh_interval=REFRESH_INTERVAL_SECONDS,
    )


@app.route("/api/quotes")
def api_quotes():
    return jsonify(fetch_all_quotes())


@app.route("/api/history/<code>")
def api_history(code):
    return jsonify(fetch_history(code.upper()))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

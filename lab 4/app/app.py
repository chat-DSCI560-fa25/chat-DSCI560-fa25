from flask import Flask, render_template, request, jsonify


app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")



@app.get("/api/portfolios")
def api_portfolios():
    return jsonify([
    {"id": 1, "name": "Tommy"},
    {"id": 2, "name": "Trojan"},
    ])


@app.post("/api/run")
def api_run():
    body = request.get_json(force=True)
    result = {
    "inputs": body,
    "kpis": {
    "portfolio_value": 105000.00,
    "total_pnl": 5000.00,
    "day_pnl": 120.55
    },
    "positions": [
    {"symbol": "AAPL", "qty": 10, "avg_cost": 170.2, "last": 175.1, "unrealized": 49.0},
    {"symbol": "MSFT", "qty": 5, "avg_cost": 405.0, "last": 410.0, "unrealized": 25.0}
    ],
    "trades": [
    {"date": "2025-06-18", "symbol": "AAPL", "side": "BUY", "qty": 10, "price": 170.2},
    {"date": "2025-06-20", "symbol": "MSFT", "side": "BUY", "qty": 5, "price": 405.0}
    ],
    "equity_curve": [
    {"date": "2025-06-17", "value": 100000},
    {"date": "2025-06-18", "value": 100950},
    {"date": "2025-06-19", "value": 101200}
    ]
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
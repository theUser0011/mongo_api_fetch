from flask import Flask, jsonify
from pymongo import MongoClient
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Flask App
# --------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------
# MongoDB Config
# --------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["options_data"]
collection = db["symbols_structural"]

# --------------------------------------------------
# Utility: Get Today's Date (IST)
# --------------------------------------------------
def get_today_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d")

# --------------------------------------------------
# Home Route (Server + DB Health Check)
# --------------------------------------------------
@app.route("/")
def home():
    try:
        client.admin.command("ping")
        return jsonify({
            "status": "success",
            "message": "Server running successfully 🚀",
            "database": "MongoDB connected successfully",
            "timestamp_ist": datetime.now(
                pytz.timezone("Asia/Kolkata")
            ).strftime("%Y-%m-%d %H:%M:%S")
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Server running, but MongoDB connection failed ❌",
            "error": str(e)
        }), 500

# --------------------------------------------------
# Fetch Today's Options Data
# --------------------------------------------------
@app.route("/api/options/today", methods=["GET"])
def get_today_options():
    today = get_today_ist()

    doc = collection.find_one(
        {"trade_date": today},
        {"_id": 0}
    )

    if not doc:
        return jsonify({
            "status": "pending",
            "trade_date": today,
            "message": "Data not loaded yet, wait for workflow loading"
        }), 202

    return jsonify({
        "status": "success",
        "trade_date": doc.get("trade_date"),
        "data": doc.get("data", {})
    }), 200

# --------------------------------------------------
# Fetch Options Data By Date
# Example: /api/options/date?date=2026-01-09
# --------------------------------------------------
@app.route("/api/options/date", methods=["GET"])
def get_options_by_date():
    from flask import request

    date_str = request.args.get("date")

    # Validate input
    if not date_str:
        return jsonify({
            "status": "error",
            "message": "Missing date parameter. Use format: /api/options/date?date=YYYY-MM-DD"
        }), 400

    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid date format. Use YYYY-MM-DD"
        }), 400

    doc = collection.find_one(
        {"trade_date": date_str},
        {"_id": 0}
    )

    if not doc:
        return jsonify({
            "status": "pending",
            "trade_date": date_str,
            "message": "Data not found for this date"
        }), 202

    return jsonify({
        "status": "success",
        "trade_date": doc.get("trade_date"),
        "data": doc.get("data", {})
    }), 200

# --------------------------------------------------
# Local Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

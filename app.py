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
# Home Route (Health Check)
# --------------------------------------------------
@app.route("/")
def home():
    try:
        # simple ping
        client.admin.command("ping")
        return jsonify({
            "status": "success",
            "message": "MongoDB connected successfully 🚀"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# --------------------------------------------------
# Fetch Today's Options Data
# --------------------------------------------------
@app.route("/api/options/today", methods=["GET"])
def get_today_options():
    today = get_today_ist()

    doc = collection.find_one(
        {"trade_date": today},
        {"_id": 0}  # hide Mongo _id
    )

    if not doc:
        return jsonify({
            "status": "pending",
            "trade_date": today,
            "message": "Data not loaded yet, wait for workflow loading"
        }), 202

    # Clean / structured response
    response = {
        "status": "success",
        "trade_date": doc.get("trade_date"),
        "data": doc.get("data", {})
    }

    return jsonify(response), 200

# --------------------------------------------------
# Vercel Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

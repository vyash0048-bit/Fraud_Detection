from flask import Flask, render_template, request, jsonify
import requests
import uuid
import logging

import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000/predict")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/score", methods=["POST"])
def score():
    try:
        data = request.json
        
        # Build the payload for FastAPI
        # For this demo, we extract specific fields, and put the rest in features
        transaction_id = data.get("transaction_id", str(uuid.uuid4()))
        features = data.get("features", {})
        
        payload = {
            "transaction_id": transaction_id,
            "features": features
        }
        
        app.logger.info(f"Sending payload to FastAPI: {payload}")
        
        response = requests.post(FASTAPI_URL, json=payload)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            app.logger.error(f"FastAPI error: {response.text}")
            return jsonify({"error": "Failed to score transaction", "details": response.text}), response.status_code
            
    except Exception as e:
        app.logger.error(f"Flask error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__, static_folder="public")

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json() or {}
    # Example placeholder logic — replace with your actual CyberSecSuite logic
    result = {
        "status": "success",
        "message": "Scan completed successfully!",
        "received_data": data
    }
    return jsonify(result)


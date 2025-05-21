#!/usr/bin/env python
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from src.routes.report_routes import report_bp
from src.routes.monitoring_routes import monitoring_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

app.config["DEBUG"] = True

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Crypto Investigator API is running!"}), 200

app.register_blueprint(report_bp, url_prefix='/api/reports')
app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

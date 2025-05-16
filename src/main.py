#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import sys
import os
from dotenv import load_dotenv # <<< ADDED THIS LINE

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables from .env file
# This should be one of the first things your app does.
dotenv_path = os.path.join(project_root, ".env") # Assuming .env is in the Crypto directory
print(f"MAIN_PY_DEBUG: Attempting to load .env file from: {dotenv_path}") # DEBUG
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print("MAIN_PY_DEBUG: .env file loaded successfully.") # DEBUG
else:
    print("MAIN_PY_DEBUG: .env file NOT FOUND at expected location.") # DEBUG

# For testing, print a specific key if it was loaded
# test_alchemy_key = os.environ.get("ALCHEMY_ETH_MAINNET_API_KEY")
# print(f"MAIN_PY_DEBUG: ALCHEMY_ETH_MAINNET_API_KEY from os.environ after load_dotenv: {test_alchemy_key}") # DEBUG

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from src.routes.report_routes import report_bp
from src.routes.monitoring_routes import monitoring_bp

app = Flask(__name__, static_folder=\'static\', static_url_path=\'\')
CORS(app)

app.config["DEBUG"] = True

@app.route(\'/\')
def serve_index():
    return send_from_directory(app.static_folder, \'index.html\')

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Crypto Investigator API is running!"}), 200

app.register_blueprint(report_bp, url_prefix=\'/api/reports\')
app.register_blueprint(monitoring_bp, url_prefix=\'/api/monitoring\')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import sys
import os

# --- Explicitly load .env file for environment variables ---
from dotenv import load_dotenv
# Construct the path to the .env file, assuming it's in the project root (Crypto/)
# main.py is in src/, so ../.env should point to Crypto/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"MAIN_PY_DEBUG: Attempting to load .env file from: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"MAIN_PY_DEBUG: .env file found and loaded from {dotenv_path}.")
else:
    print(f"MAIN_PY_DEBUG: .env file NOT found at {dotenv_path}. Environment variables might not be set as expected.")
# --- End of .env loading ---

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_from_directory # Added send_from_directory
from flask_cors import CORS

from src.routes.report_routes import report_bp
from src.routes.monitoring_routes import monitoring_bp

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app) # Enable CORS for all routes, allowing frontend from different origin

# Basic configuration (can be expanded)
app.config["DEBUG"] = True # Set to False in production

# Route to serve the index.html from the static folder at the root URL
@app.route('/')
def serve_index():
    # app.static_folder is 'static', which is relative to app.root_path (src/)
    # This will serve src/static/index.html
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Crypto Investigator API is running!"}), 200

# Register Blueprints
app.register_blueprint(report_bp, url_prefix='/api/reports')
app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')

if __name__ == "__main__":
    # IMPORTANT: For deployment on free tiers, host is often set to '0.0.0.0'
    # and port might be dynamically assigned or set via environment variable (e.g., PORT).
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


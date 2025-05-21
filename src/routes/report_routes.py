from flask import Blueprint, request, jsonify
import os
import json
import requests
from datetime import datetime

# Import API keys from config.py instead of environment variables
from src.config import ETHERSCAN_API_KEY, ALCHEMY_ETH_MAINNET_API_KEY

# Create blueprint
report_bp = Blueprint('reports', __name__)

# Debug print statements to verify API keys are loaded
print(f"DEBUG_REPORT_ROUTES: ETHERSCAN_API_KEY from config: {ETHERSCAN_API_KEY}")
print(f"DEBUG_REPORT_ROUTES: ALCHEMY_ETH_MAINNET_API_KEY from config: {ALCHEMY_ETH_MAINNET_API_KEY}")

# Keep the rest of the file unchanged

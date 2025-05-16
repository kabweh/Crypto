#!/home/ubuntu/crypto_investigator_app/venv/bin/python
from flask import Blueprint, jsonify, request
import os

# Assuming monitoring_service.py is in src.services
# Adjust the import path if your structure is different
from src.services.monitoring_service import fetch_ethereum_latest_block_transactions, analyze_transaction_for_suspicious_activity

monitoring_bp = Blueprint("monitoring_bp", __name__)

# --- Store last processed block to avoid reprocessing (in-memory for now, consider persistence) ---
last_processed_block_eth = None

@monitoring_bp.route("/check-ethereum-now", methods=["POST"])
def check_ethereum_realtime():
    """Endpoint to manually trigger a check of the latest Ethereum block for suspicious activity."""
    global last_processed_block_eth

    result = fetch_ethereum_latest_block_transactions()
    
    if result["status"] != "success":
        return jsonify({"status": "error", "message": result["message"], "source": result.get("source")}), 502

    block_number_hex = result.get("block_number")
    if block_number_hex is None:
        return jsonify({"status": "error", "message": "Could not retrieve block number from Alchemy response."}), 500
    
    try:
        current_block_number = int(block_number_hex, 16)
    except ValueError:
        return jsonify({"status": "error", "message": f"Invalid block number format received: {block_number_hex}"}), 500

    # Basic check to avoid reprocessing the same block if called rapidly
    # A more robust solution would involve persistent storage of last_processed_block_eth
    if last_processed_block_eth == current_block_number:
        return jsonify({"status": "success", "message": f"Block {current_block_number} already processed. No new transactions to analyze.", "findings": []}), 200

    transactions = result["data"]
    all_findings = []
    processed_tx_hashes = set() # To avoid double-counting if a tx appears multiple times in a block (rare)

    for tx in transactions:
        tx_hash = tx.get("hash")
        if tx_hash and tx_hash not in processed_tx_hashes:
            findings = analyze_transaction_for_suspicious_activity(tx, "ethereum")
            if findings:
                all_findings.extend(findings)
            processed_tx_hashes.add(tx_hash)
    
    last_processed_block_eth = current_block_number

    if not all_findings:
        return jsonify({"status": "success", "message": f"Analyzed {len(transactions)} transactions in Ethereum block {current_block_number}. No suspicious activity detected by current rules.", "block_number": current_block_number, "source": result.get("source")}), 200
    
    return jsonify({
        "status": "success", 
        "message": f"Analyzed {len(transactions)} transactions in Ethereum block {current_block_number}. Suspicious activities found.",
        "block_number": current_block_number,
        "findings": all_findings,
        "source": result.get("source")
    }), 200

# Future: Add endpoints for starting/stopping continuous monitoring (if implemented)
# Future: Add endpoints for other chains


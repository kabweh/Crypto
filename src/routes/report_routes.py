#!/home/ubuntu/crypto_investigator_app/venv/bin/python
from flask import Blueprint, request, jsonify
import requests # For making API calls to blockchain explorers
import os
import time # For potential rate limiting delays

report_bp = Blueprint("report_bp", __name__)

# --- Configuration for Blockchain APIs (using environment variables is best practice) ---
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "YOUR_FREE_ETHERSCAN_API_KEY")
ALCHEMY_ETH_MAINNET_API_KEY = os.environ.get("ALCHEMY_ETH_MAINNET_API_KEY", "YOUR_FREE_ALCHEMY_API_KEY")
BLOCKCHAIN_INFO_API_KEY = os.environ.get("BLOCKCHAIN_INFO_API_KEY") # Blockchain.com often doesn't require a key for basic public data
BSCSCAN_API_KEY = os.environ.get("BSCSCAN_API_KEY", "YOUR_FREE_BSCSCAN_API_KEY")
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "YOUR_FREE_HELIUS_API_KEY")

# --- Helper function to get Ethereum wallet transactions ---
def get_ethereum_wallet_transactions(wallet_address):
    # Try Alchemy first due to its generous free tier and robust API
    if ALCHEMY_ETH_MAINNET_API_KEY and ALCHEMY_ETH_MAINNET_API_KEY != "YOUR_FREE_ALCHEMY_API_KEY":
        api_url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_ETH_MAINNET_API_KEY}"
        payload_from = {
            "jsonrpc": "2.0", "id": 1, "method": "alchemy_getAssetTransfers",
            "params": [{"fromBlock": "0x0", "toBlock": "latest", "fromAddress": wallet_address,
                       "category": ["external", "internal", "erc20", "erc721", "erc1155"],
                       "withMetadata": True, "excludeZeroValue": True, "maxCount": "0x64"
            }]
        }
        payload_to = {
            "jsonrpc": "2.0", "id": 2, "method": "alchemy_getAssetTransfers",
            "params": [{"fromBlock": "0x0", "toBlock": "latest", "toAddress": wallet_address,
                       "category": ["external", "internal", "erc20", "erc721", "erc1155"],
                       "withMetadata": True, "excludeZeroValue": True, "maxCount": "0x64"
            }]
        }
        try:
            response_from = requests.post(api_url, json=payload_from)
            response_from.raise_for_status()
            data_from = response_from.json().get("result", {}).get("transfers", [])
            time.sleep(0.2)
            response_to = requests.post(api_url, json=payload_to)
            response_to.raise_for_status()
            data_to = response_to.json().get("result", {}).get("transfers", [])
            all_transactions = data_from + data_to
            seen_hashes = set()
            unique_transactions = []
            for tx in all_transactions:
                tx_hash = tx.get("hash")
                log_index = tx.get("logIndex")
                unique_id = tx.get("uniqueId")
                identifier = f"{tx_hash}-{log_index}" if log_index is not None else unique_id
                if identifier not in seen_hashes:
                    unique_transactions.append(tx)
                    seen_hashes.add(identifier)
            unique_transactions.sort(key=lambda x: (int(x.get("blockNum", 0), 16) if isinstance(x.get("blockNum"), str) else x.get("blockNum",0) , x.get("transactionIndex", 0), x.get("logIndex", 0) ), reverse=True)
            return {"status": "success", "data": unique_transactions[:100], "source": "Alchemy"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e), "source": "Alchemy"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred with Alchemy: {str(e)}", "source": "Alchemy"}
    elif ETHERSCAN_API_KEY and ETHERSCAN_API_KEY != "YOUR_FREE_ETHERSCAN_API_KEY":
        api_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey={ETHERSCAN_API_KEY}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "1":
                return {"status": "success", "data": data["result"], "source": "Etherscan"}
            else:
                etherscan_result_message = data.get('result', '.')
                return {"status": "error", "message": data.get("message", "Failed to fetch data or no transactions found.") + f" (Etherscan message: {etherscan_result_message})", "source": "Etherscan"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e), "source": "Etherscan"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred with Etherscan: {str(e)}", "source": "Etherscan"}
    else:
        return {"status": "error", "message": "Neither Alchemy nor Etherscan API key is configured. Please configure at least one.", "source": "Configuration Error"}

# --- Helper function to get Bitcoin wallet transactions (Example with Blockchain.info) ---
def get_bitcoin_wallet_transactions(wallet_address):
    api_url = f"https://blockchain.info/rawaddr/{wallet_address}?limit=50"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return {"status": "success", "data": data.get("txs", []), "address_info": {k: data[k] for k in (
"hash160", "address", "n_tx", "n_unredeemed", "total_received", "total_sent", "final_balance") if k in data}, "source": "Blockchain.info"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500 and "Unsupported Address Format" in e.response.text:
             return {"status": "error", "message": "Unsupported or invalid Bitcoin address format.", "source": "Blockchain.info"}
        if e.response.status_code == 404:
            return {"status": "error", "message": "Bitcoin address not found or no transactions.", "source": "Blockchain.info"}
        return {"status": "error", "message": f"HTTP error fetching Bitcoin data: {str(e)} - {e.response.text}", "source": "Blockchain.info"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request error fetching Bitcoin data: {str(e)}", "source": "Blockchain.info"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred with Blockchain.info: {str(e)}", "source": "Blockchain.info"}

# --- Helper function to get BSC wallet transactions (Example with BscScan) ---
def get_bsc_wallet_transactions(wallet_address):
    if not BSCSCAN_API_KEY or BSCSCAN_API_KEY == "YOUR_FREE_BSCSCAN_API_KEY":
        return {"status": "error", "message": "BscScan API key not configured.", "source": "Configuration Error"}
    api_url = f"https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey={BSCSCAN_API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "1":
            return {"status": "success", "data": data["result"], "source": "BscScan"}
        else:
            bsc_scan_result_message = data.get('result', '.')
            return {"status": "error", "message": data.get("message", "Failed to fetch data or no transactions found.") + f" (BscScan message: {bsc_scan_result_message})", "source": "BscScan"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e), "source": "BscScan"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred with BscScan: {str(e)}", "source": "BscScan"}

# --- Helper function to get Solana wallet transactions (Example with Helius) ---
def get_solana_wallet_transactions(wallet_address):
    if not HELIUS_API_KEY or HELIUS_API_KEY == "YOUR_FREE_HELIUS_API_KEY":
        return {"status": "error", "message": "Helius API key not configured for Solana.", "source": "Configuration Error"}
    api_url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={HELIUS_API_KEY}&limit=50"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return {"status": "success", "data": data, "source": "Helius"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
             return {"status": "error", "message": "Solana address not found or no transactions.", "source": "Helius"}
        error_detail = "Unknown error"
        try:
            error_detail = e.response.json().get("error", e.response.text)
        except:
            error_detail = e.response.text
        return {"status": "error", "message": f"HTTP error fetching Solana data: {str(e)} - {error_detail}", "source": "Helius"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request error fetching Solana data: {str(e)}", "source": "Helius"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred with Helius: {str(e)}", "source": "Helius"}


@report_bp.route("/on-demand", methods=["POST"])
def generate_on_demand_report():
    data = request.get_json()
    if not data or "identifier" not in data or "chain" not in data:
        return jsonify({"status": "error", "message": "Missing identifier (wallet/tx hash) or chain"}), 400

    identifier = data["identifier"]
    chain = data["chain"].lower()
    report_type = data.get("type", "wallet")

    report_data = {
        "identifier": identifier,
        "chain": chain,
        "report_type": report_type,
        "details": None,
        "error": None,
        "source": None
    }

    result = None
    if report_type == "wallet":
        if chain == "ethereum":
            result = get_ethereum_wallet_transactions(identifier)
        elif chain == "bitcoin":
            result = get_bitcoin_wallet_transactions(identifier)
        elif chain == "bsc":
            result = get_bsc_wallet_transactions(identifier)
        elif chain == "solana":
            result = get_solana_wallet_transactions(identifier)
        else:
            report_data["error"] = f"Unsupported blockchain for wallet report: {chain}"
            return jsonify(report_data), 400
    elif report_type == "transaction":
        report_data["error"] = f"Transaction-specific reports are not yet implemented for {chain}."
        return jsonify(report_data), 501
    else:
        report_data["error"] = f"Invalid report type: {report_type}"
        return jsonify(report_data), 400

    if result and result["status"] == "success":
        report_data["details"] = result["data"]
        report_data["source"] = result["source"]
        if "address_info" in result:
            report_data["address_info"] = result["address_info"]
        return jsonify(report_data), 200
    elif result:
        report_data["error"] = result["message"]
        report_data["source"] = result["source"]
        if "API key not configured" in result["message"] or "Unsupported or invalid" in result["message"]:
            return jsonify(report_data), 400
        return jsonify(report_data), 502
    else:
        report_data["error"] = "An unexpected error occurred processing the report request."
        return jsonify(report_data), 500


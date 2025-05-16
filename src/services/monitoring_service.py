
#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import os
import requests
import time

ALCHEMY_ETH_MAINNET_API_KEY = os.environ.get("ALCHEMY_ETH_MAINNET_API_KEY", "YOUR_FREE_ALCHEMY_API_KEY")

# --- Configuration for Detection Rules ---
ETH_LARGE_TRANSFER_THRESHOLD = 100  # Example: 100 ETH

def fetch_ethereum_latest_block_transactions():
    """Fetches transactions from the latest Ethereum block using Alchemy."""
    if not ALCHEMY_ETH_MAINNET_API_KEY or ALCHEMY_ETH_MAINNET_API_KEY == "YOUR_FREE_ALCHEMY_API_KEY":
        return {"status": "error", "message": "Alchemy API key not configured for Ethereum monitoring.", "source": "Configuration Error"}

    api_url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_ETH_MAINNET_API_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBlockByNumber",
        "params": ["latest", True]  # True to get full transaction objects
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        if "result" in data and data["result"] and "transactions" in data["result"]:
            return {"status": "success", "data": data["result"]["transactions"], "block_number": data["result"].get("number"), "source": "Alchemy"}
        elif "error" in data:
            return {"status": "error", "message": data["error"].get("message", "Failed to fetch latest block from Alchemy."), "source": "Alchemy"}
        else:
            return {"status": "error", "message": "No transactions found in the latest block or unexpected response.", "source": "Alchemy"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e), "source": "Alchemy"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred with Alchemy: {str(e)}", "source": "Alchemy"}

def detect_large_transfer_ethereum(transaction):
    """Detects if an Ethereum transaction is a large transfer."""
    try:
        value_wei = int(transaction.get("value", "0x0"), 16)
        value_eth = value_wei / (10**18)
        if value_eth >= ETH_LARGE_TRANSFER_THRESHOLD:
            return {
                "type": "large_transfer",
                "message": f"Large ETH transfer detected: {value_eth:.2f} ETH",
                "details": {
                    "hash": transaction.get("hash"),
                    "from": transaction.get("from"),
                    "to": transaction.get("to"),
                    "value_eth": value_eth
                }
            }
    except Exception as e:
        # Log error or handle appropriately
        print(f"Error processing transaction for large transfer detection: {e}")
    return None


def analyze_transaction_for_suspicious_activity(transaction, chain):
    """Analyzes a single transaction for various suspicious activities based on the chain."""
    findings = []
    if chain == "ethereum":
        large_transfer = detect_large_transfer_ethereum(transaction)
        if large_transfer:
            findings.append(large_transfer)
        
        # Placeholder for other Ethereum detection rules:
        # - Interactions with known scam contracts
        # - Tornado Cash usage
        # - Newly deployed tokens (rug pull/honeypot signs)
        # - Drained wallets or unusual transaction patterns

    # elif chain == "bitcoin":
    #     # Bitcoin specific detection rules
    # elif chain == "bsc":
    #     # BSC specific detection rules
    # elif chain == "solana":
    #     # Solana specific detection rules

    return findings


# Example of how this might be used in a monitoring loop (conceptual)
# def continuous_monitoring_ethereum():
#     while True:
#         result = fetch_ethereum_latest_block_transactions()
#         if result["status"] == "success":
#             for tx in result["data"]:
#                 findings = analyze_transaction_for_suspicious_activity(tx, "ethereum")
#                 if findings:
#                     print(f"Suspicious activity found: {findings}") # Replace with actual alerting
#         else:
#             print(f"Error fetching transactions: {result["message"]}")
#         time.sleep(15) # Poll every 15 seconds (adjust based on API limits and needs)


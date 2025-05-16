#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import os

# --- Risk Scoring Configuration ---
# Base scores for different types of suspicious activities
RISK_SCORE_FACTORS = {
    "large_transfer": 20,  # Base score for any large transfer
    "interacts_with_known_scam_address": 70, # High risk
    "uses_mixer_service": 60, # e.g., Tornado Cash (detection logic to be added)
    "potential_rug_pull_token": 80, # (detection logic to be added)
    "honeypot_contract": 75, # (detection logic to be added)
    "drained_wallet_activity": 50, # (detection logic to be added)
    "unusual_transaction_pattern": 30, # (detection logic to be added)
    "newly_deployed_high_volume_token": 40, # Suspicious but needs more context
    # Add more factors as detection capabilities are built
}

# Multipliers (examples, can be refined)
VALUE_MULTIPLIER_ETH = {
    100: 1.0,    # 100 ETH
    500: 1.2,    # 500 ETH
    1000: 1.5,   # 1000 ETH
    5000: 2.0    # 5000+ ETH
}

# --- Summary Generation Templates ---
SUMMARY_TEMPLATES = {
    "large_transfer": "A significantly large transfer of {value_eth:.2f} {currency} from {from_address} to {to_address} was detected on the {chain} blockchain. Transaction hash: {tx_hash}.",
    "interacts_with_known_scam_address": "A transaction involving address {involved_address} (which is on a known scam list) was detected on the {chain} blockchain. Transaction hash: {tx_hash}. This is a high-risk activity.",
    "uses_mixer_service": "Address {address} appears to have interacted with a known mixer service ({mixer_name}) on the {chain} blockchain. Transaction hash: {tx_hash}. This could be an attempt to obscure transaction origins.",
    "default_finding": "Suspicious activity of type 
{finding_type}
 was detected on the {chain} blockchain. Details: {details_str}"
}

def calculate_risk_score(findings):
    """
    Calculates a risk score based on a list of findings.
    Each finding is a dictionary with at least a 
'type'
 and 
'details'
 key.
    """
    total_risk_score = 0
    if not findings:
        return 0

    for finding in findings:
        finding_type = finding.get("type")
        details = finding.get("details", {})
        base_score = RISK_SCORE_FACTORS.get(finding_type, 10) # Default score for unknown types

        # Apply multipliers or adjustments based on details
        if finding_type == "large_transfer":
            value_eth = details.get("value_eth", 0)
            multiplier = 1.0
            for threshold, mult in sorted(VALUE_MULTIPLIER_ETH.items(), reverse=True):
                if value_eth >= threshold:
                    multiplier = mult
                    break
            base_score *= multiplier
        
        # Add other specific adjustments here

        total_risk_score += base_score
    
    # Cap score at 100
    return min(int(total_risk_score), 100)

def generate_summary_for_finding(finding):
    """
    Generates a human-readable summary for a single finding.
    """
    finding_type = finding.get("type")
    details = finding.get("details", {})
    chain = details.get("chain", "UnknownChain").upper()
    currency = "ETH" if chain == "ETHEREUM" else "tokens/native currency" # Basic currency assumption

    template = SUMMARY_TEMPLATES.get(finding_type, SUMMARY_TEMPLATES["default_finding"])
    
    # Prepare details for formatting
    format_params = {
        "finding_type": finding_type,
        "details_str": str(details),
        "chain": chain,
        "currency": currency,
        "value_eth": details.get("value_eth"),
        "from_address": details.get("from"),
        "to_address": details.get("to"),
        "tx_hash": details.get("hash", details.get("transaction_hash")),
        "involved_address": details.get("address", details.get("interacting_address")),
        "mixer_name": details.get("mixer_name", "Unknown Mixer"),
        "address": details.get("address")
    }

    try:
        return template.format(**format_params)
    except KeyError as e:
        print(f"KeyError generating summary for {finding_type}: {e}. Using default.")
        return SUMMARY_TEMPLATES["default_finding"].format(finding_type=finding_type, details_str=str(details), chain=chain)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary for finding type {finding_type}."

def generate_overall_summary_and_risk(all_findings):
    """
    Generates an overall summary and calculates a final risk score for a list of findings 
    (e.g., from a single transaction or a block of transactions).
    """
    if not all_findings:
        return "No suspicious activities detected by current rules.", 0

    overall_risk_score = calculate_risk_score(all_findings)
    
    summaries = []
    for finding in all_findings:
        summaries.append(generate_summary_for_finding(finding))
    
    # Combine summaries into a single report
    # For now, just join them. Could be more sophisticated.
    combined_summary = "\n\n---\n\n".join(summaries)
    
    # Add a header with the overall risk score
    final_report_summary = f"**Overall Risk Score: {overall_risk_score}/100**\n\n{combined_summary}"
    
    return final_report_summary, overall_risk_score

# Example Usage (can be called from monitoring_service.py or report_routes.py):
# if __name__ == "__main__":
#     mock_findings_list = [
#         {
#             "type": "large_transfer",
#             "details": {
#                 "hash": "0x123abc...", "from": "0xsender...", "to": "0xreceiver...",
#                 "value_eth": 150.75, "chain": "ethereum"
#             }
#         },
#         {
#             "type": "interacts_with_known_scam_address",
#             "details": {
#                 "transaction_hash": "0x456def...", "interacting_address": "0xscammer...",
#                 "chain": "bsc"
#             }
#         }
#     ]
#     summary, risk = generate_overall_summary_and_risk(mock_findings_list)
#     print("--- Generated Report ---")
#     print(summary)
#     print(f"\n--- Final Risk Score: {risk} ---")


#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import os
import requests # For Discord Webhooks and potentially other HTTP-based alerts

# --- Configuration for Alerting Services (using environment variables is best practice) ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "YOUR_SENDGRID_API_KEY")
ALERT_EMAIL_FROM = os.environ.get("ALERT_EMAIL_FROM", "alerts@example.com")
ALERT_EMAIL_TO = os.environ.get("ALERT_EMAIL_TO", "user@example.com")

def send_telegram_alert(message):
    """Sends an alert message via Telegram Bot."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or \
       not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("Telegram bot token or chat ID not configured. Skipping Telegram alert.")
        return False
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown" # Or "HTML"
    }
    try:
        response = requests.post(api_url, data=payload)
        response.raise_for_status()
        print(f"Telegram alert sent: {message[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram alert: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while sending Telegram alert: {e}")
        return False

def send_discord_alert(message, embed=None):
    """Sends an alert message via Discord Webhook. Embeds can be used for richer messages."""
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL":
        print("Discord webhook URL not configured. Skipping Discord alert.")
        return False

    payload = {
        "content": message
    }
    if embed:
        payload["embeds"] = [embed] # Discord expects embeds to be a list

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Discord alert sent: {message[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord alert: {e} - Response: {e.response.text if e.response else 'No response'}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while sending Discord alert: {e}")
        return False

def send_email_alert(subject, body_html):
    """Sends an email alert using SendGrid (or a similar free email API)."""
    if not SENDGRID_API_KEY or SENDGRID_API_KEY == "YOUR_SENDGRID_API_KEY":
        print("SendGrid API key not configured. Skipping email alert.")
        return False
    
    # This is a simplified example for SendGrid. Actual implementation might use their Python library.
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # message = Mail(
    #     from_email=ALERT_EMAIL_FROM,
    #     to_emails=ALERT_EMAIL_TO,
    #     subject=subject,
    #     html_content=body_html)
    # try:
    #     sg = SendGridAPIClient(SENDGRID_API_KEY)
    #     response = sg.send(message)
    #     print(f"Email alert sent via SendGrid, status code: {response.status_code}")
    #     return True
    # except Exception as e:
    #     print(f"Error sending email alert via SendGrid: {e}")
    #     return False
    print(f"Email alert (simulated): Subject: {subject}, Body: {body_html[:100]}...")
    print("Actual email sending with SendGrid needs the `sendgrid` library and proper setup.")
    return True # Simulate success for now

def dispatch_alert(finding_type, details):
    """
    Dispatches an alert through configured channels based on the finding.
    `details` should be a dictionary containing information about the suspicious activity.
    """
    message = f"🚨 Suspicious Activity Detected! 🚨\nType: {finding_type}\n"
    
    if "hash" in details:
        message += f"Transaction Hash: {details["hash"]}\n"
    if "address" in details:
        message += f"Address: {details["address"]}\n"
    if "from" in details and "to" in details and "value_eth" in details:
        message += f"From: {details["from"]}\nTo: {details["to"]}\nValue: {details["value_eth"]:.2f} ETH\n"
    if "reason" in details:
        message += f"Reason: {details["reason"]}\n"
    if "chain" in details:
        message += f"Chain: {details["chain"].upper()}\n"

    # Add more details to the message as needed
    message += f"\nDetails: {str(details)}"

    # Send to preferred channels (e.g., Telegram first)
    telegram_sent = send_telegram_alert(message)
    discord_sent = send_discord_alert(message) # Basic message, can be enhanced with embeds
    
    # Optionally send email
    # email_subject = f"Crypto Alert: {finding_type} on {details.get('chain', '').upper()}"
    # email_body = message.replace("\n", "<br>")
    # email_sent = send_email_alert(email_subject, email_body)

    if telegram_sent or discord_sent: # or email_sent:
        print("Alert dispatched successfully to one or more channels.")
    else:
        print("Failed to dispatch alert to any channel.")

# Example Usage (can be called from monitoring_service.py when a finding occurs):
# if __name__ == "__main__":
#     # Mock finding for testing
#     mock_finding = {
#         "type": "large_transfer_test",
#         "details": {
#             "hash": "0x123abc...",
#             "from": "0xsender...",
#             "to": "0xreceiver...",
#             "value_eth": 150.75,
#             "chain": "ethereum"
#         }
#     }
#     dispatch_alert(mock_finding["type"], mock_finding["details"])

#     mock_scam_finding = {
#         "type": "scam_address_interaction_test",
#         "details": {
#             "transaction_hash": "0x456def...",
#             "interacting_address": "0xscammer...",
#             "our_monitored_address": "0xvictim...",
#             "chain": "bsc",
#             "reason": "Interaction with known scam address."
#         }
#     }
#     dispatch_alert(mock_scam_finding["type"], mock_scam_finding["details"])



import requests
import json

# Paste your n8n Test Webhook URL here
WEBHOOK_URL = "https://autotesting.app.n8n.cloud/webhook/feedback-analysis"

# Sample customer feedback
payload = {
    "feedback": (
        "My order is three days late. "
        "The tracking page has not updated and "
        "customer support is not responding."
    )
}

try:
    print("Sending request to n8n...")

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=120
    )

    print("\nHTTP Status:", response.status_code)

    print("\nResponse from n8n:")

    try:
        print(json.dumps(response.json(), indent=4))
    except ValueError:
        print(response.text)

except requests.exceptions.RequestException as error:
    print("\nRequest failed:", error)

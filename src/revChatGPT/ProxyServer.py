"""
Fetches cookies from chat.openai.com and returns them (Flask)
"""
from OpenAIAuth.Cloudflare import Cloudflare
from flask import Flask, request, jsonify
import tls_client
import json

app = Flask(__name__)

session = tls_client.Session(
    client_identifier="chrome_108"
)

# Get cloudflare cookies
cf_clearance, user_agent = Cloudflare().get_cf_cookies()

@app.route('/backend-api/conversation', methods=['POST'])
def conversation():
    # Get cookies from request
    cookies = {
        "cf_clearance": cf_clearance,
        "__Secure-next-auth.session-token": request.cookies.get("__Secure-next-auth.session-token"),
    }
    # Get JSON payload from request
    payload = request.get_json()

    # Set user agent
    headers ={
        "Accept": "text/event-stream",
        "Authorization": request.headers.get("Authorization"),
        "User-Agent": user_agent,
        "Content-Type": "application/json",
        "X-Openai-Assistant-App-Id": "",
        "Connection": "close",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://chat.openai.com/chat",
    }

    # Send request to OpenAI
    response = session.post(
        url="https://chat.openai.com/backend-api/conversation",
        headers=headers,
        cookies=cookies,
        data=json.dumps(payload),
        timeout_seconds=360
    )

    # Return response
    return response.text

if __name__ == '__main__':
    app.run(debug=True)

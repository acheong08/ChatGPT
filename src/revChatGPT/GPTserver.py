from flask import Flask
from flask import jsonify
from flask import request
from revChatGPT.ChatGPT import Chatbot

app = Flask(__name__)

token_available = {}
chatbot = Chatbot(no_refresh=True)

def verify_request_data(data: dict) -> bool:
    """
    Verifies that the required fields are present in the data.
    """
    # Required fields: "prompt", "session_token"
    if "prompt" not in data or "session_token" not in data:
        return False
    return True

@app.route("/chat", methods=["POST"])
def chat():
    """
    The main chat endpoint.
    """
    data = request.get_json()
    if not verify_request_data(data):
        return jsonify({"error": "Invalid data."}), 400

    # Return rate limit if token_available is false
    if token_available.get(data.get("session_token"), True) is False:
        return jsonify({"error": "Rate limited"}), 429

    token_available[data.get("session_token")] = False

    try:
        response = chatbot.ask(prompt=data["prompt"], session_token=data["session_token"], parent_id=data.get("parent_id"), conversation_id=data.get("conversation_id"))
    except Exception as exc:
        token_available[data.get("session_token")] = True
        return jsonify({"error": str(exc)}), 500

    response["session_token"] = chatbot.session_token
    token_available[data.get("session_token")] = True

    return jsonify(response), 200

@app.route("/refresh", methods=["POST"])
def refresh():
    """
    The refresh endpoint.
    """
    data = request.get_json()
    if "session_token" not in data:
        return jsonify({"error": "Invalid data."}), 400

    if data.get("session_token") not in token_available:
        return jsonify({"error": "Invalid token."}), 400

    chatbot.session_token = data["session_token"]
    try:
        chatbot.refresh_session()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"session_token": chatbot.session_token}), 200

def main():
    app.run(host="127.0.0.1", port=8080)

from flask import Flask, request, jsonify

import time

from revChatGPT.ChatGPT import Chatbot

app = Flask(__name__)

# Session token based rate limiting
token_available: dict = {}

chatbot = Chatbot(config={"session_token": "None"},
                  conversation_id=None, parent_id=None, no_refresh=True)

def verify_data(data: dict) -> bool:
    """
    Verifies that the required fields are present in the data.
    """
    # Required fields: "message", "session_token"
    if "prompt" not in data or "session_token" not in data:
        return False
    return True


@app.route('/chat', methods=['POST'])
def chat():
    """
    The main chat endpoint.
    """
    data: dict = request.get_json()
    if not verify_data(data=data):
        return jsonify({"error": "Invalid data."}), 400

    chatbot.session_token: str = data["session_token"]

    conversation_id = data.get("conversation_id", None)
    parent_id = data.get("parent_id", None)

    # Return rate limit if token_available is false
    if token_available.get(data.get("session_token")) != None and not token_available.get(data.get("session_token")):
        return jsonify({"error": "Rate limited"}), 429
    
    token_available[data.get("session_token")] = False

    try:
        response = chatbot.ask(
            prompt=data["prompt"], session_token=data["session_token"], parent_id=parent_id, conversation_id=conversation_id)
    except Exception as exc:
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

    chatbot.session_token = data["session_token"]
    try:
        chatbot.refresh_session()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"session_token": chatbot.session_token}), 200


def main():
    app.run(host="127.0.0.1", port=8080)

import json
import uuid

import httpx


class Chatbot:
    config: json
    conversation_id: str
    parent_id: str
    headers: dict

    def __init__(self, config, conversation_id=None):
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = self.generate_uuid()
        self.refresh_headers()

    def reset_chat(self):
        self.conversation_id = None
        self.parent_id = self.generate_uuid()

    def refresh_headers(self):
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.config["Authorization"],
            "Content-Type": "application/json",
        }

    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return uid

    async def get_chat_response(self, prompt):
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(self.generate_uuid()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                }
            ],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_id,
            "model": "text-davinci-002-render",
        }
        async with httpx.AsyncClient(proxies="http://localhost:7890") as client:
            response = await client.post(
                "https://chat.openai.com/backend-api/conversation",
                headers=self.headers,
                data=json.dumps(data),
            )
            print(response)
        try:
            response = response.text.splitlines()[-4]
        except:
            print(response.text)
            return ValueError("Error: Response is not a text/event-stream")
        try:
            response = response[6:]
        except:
            print(response.text)
            return ValueError("Response is not in the correct format")
        response = json.loads(response)
        self.parent_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        message = response["message"]["content"]["parts"][0]
        return {
            "message": message,
            "conversation_id": self.conversation_id,
            "parent_id": self.parent_id,
        }

    async def refresh_session(self):
        if "session_token" not in self.config:
            return ValueError("No session token provided")
        cookies = {"__Secure-next-auth.session-token": self.config["session_token"]}
        async with httpx.AsyncClient(cookies=cookies, proxies="http://localhost:7890") as client:
            response = await client.get("https://chat.openai.com/api/auth/session")
        try:
            self.config["session_token"] = response.cookies.get(
                "__Secure-next-auth.session-token"
            )
            self.config["Authorization"] = response.json()["accessToken"]
            self.refresh_headers()
        except Exception as e:
            print("Error refreshing session")
            print(response.text)

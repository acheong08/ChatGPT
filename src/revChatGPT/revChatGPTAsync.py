# Author: @acheong08@fosstodon.org
# License: MIT
# Description: A Python wrapper for OpenAI's chatbot API
import json
import uuid
import asyncio

import httpx

from OpenAIAuth.OpenAIAuth import OpenAIAuth, Debugger


def generate_uuid() -> str:
    uid = str(uuid.uuid4())
    return uid


class Chatbot:
    config: json
    conversation_id: str
    parent_id: str
    headers: dict
    conversation_id_prev: str
    parent_id_prev: str

    def __init__(self, config, conversation_id=None, debug=False, refresh=True) -> Exception:
        self.debugger = Debugger(debug)
        self.debug = debug
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = generate_uuid()
        if "session_token" in config or ("email" in config and "password" in config) and refresh:
            self.refresh_session()
        if "Authorization" in config:
            self.refresh_headers()

    # Resets the conversation ID and parent ID
    def reset_chat(self) -> None:
        self.conversation_id = None
        self.parent_id = generate_uuid()

    # Refreshes the headers -- Internal use only
    def refresh_headers(self) -> None:
        if "Authorization" not in self.config:
            self.config["Authorization"] = ""
        elif self.config["Authorization"] is None:
            self.config["Authorization"] = ""
        self.headers = {
            "Host": "chat.openai.com",
            "Accept": "text/event-stream",
            "Authorization": "Bearer " + self.config["Authorization"],
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.1 Safari/605.1.15",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
        }

    # Generates a UUID -- Internal use only

    # Generator for chat stream -- Internal use only
    async def get_chat_stream(self, data) -> None:
        s = httpx.AsyncClient()
        async with s.stream(
            'POST', 
            "https://chat.openai.com/backend-api/conversation",
            headers=self.headers,
            data=json.dumps(data),
            timeout=100,
        )as response:
            async for line in response.aiter_lines():
                try:
                    if line == "":
                        continue
                    line = line[6:]
                    line = json.loads(line)
                    try:
                        message = line["message"]["content"]["parts"][0]
                        self.conversation_id = line["conversation_id"]
                        self.parent_id = line["message"]["id"]
                    except:
                        continue
                    yield {
                        "message": message,
                        "conversation_id": self.conversation_id,
                        "parent_id": self.parent_id,
                    }
                except:
                    continue

    # Gets the chat response as text -- Internal use only
    async def get_chat_text(self, data) -> dict:
        # Create request session
        s = httpx.Client(http2=True)
        async with httpx.AsyncClient() as s:
            # set headers
            s.headers = self.headers
            # Set multiple cookies
            if "session_token" in self.config:
                s.cookies.set(
                    "__Secure-next-auth.session-token",
                    self.config["session_token"],
                )
            s.cookies.set(
                "__Secure-next-auth.callback-url",
                "https://chat.openai.com/",
            )
            # Set proxies
            if self.config.get("proxy", "") != "":
                s.proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"],
                }
            response = await s.post(
                "https://chat.openai.com/backend-api/conversation",
                data=json.dumps(data),
                timeout=60,
            )
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except Exception as exc:
                self.debugger.log("Incorrect response from OpenAI API")
                self.debugger.log(response.text)
                try:
                    resp = response.json()
                    if resp['detail']['code'] == "invalid_api_key":
                        if "email" in self.config and "password" in self.config:
                            self.refresh_session()
                            return self.get_chat_text(data)
                        else:
                            raise Exception(
                                "Missing necessary credentials") from exc
                except Exception as exc2:
                    raise Exception("Not a JSON response") from exc2
                raise Exception("Incorrect response from OpenAI API") from exc
            response = json.loads(response)
            self.parent_id = response["message"]["id"]
            self.conversation_id = response["conversation_id"]
            message = response["message"]["content"]["parts"][0]
            return {
                "message": message,
                "conversation_id": self.conversation_id,
                "parent_id": self.parent_id,
            }

    # Gets the chat response
    async def get_chat_response(self, prompt, output="text") -> dict or None:
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(generate_uuid()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_id,
            "model": "text-davinci-002-render",
        }
        self.conversation_id_prev = self.conversation_id
        self.parent_id_prev = self.parent_id
        if output == "text":
            return await self.get_chat_text(data)
        elif output == "stream":
            return self.get_chat_stream(data)
        else:
            raise ValueError("Output must be either 'text' or 'stream'")

    def rollback_conversation(self) -> None:
        self.conversation_id = self.conversation_id_prev
        self.parent_id = self.parent_id_prev

    def refresh_session(self) -> Exception:
        if (
            "session_token" not in self.config
            and ("email" not in self.config or "password" not in self.config)
            and "Authorization" not in self.config
        ):
            error = ValueError("No tokens provided")
            self.debugger.log(error)
            raise error
        elif "session_token" in self.config:
            if (
                self.config["session_token"] is None
                or self.config["session_token"] == ""
            ):
                raise ValueError("No tokens provided")
            s = httpx.Client(http2=True)
            if self.config.get("proxy", "") != "":
                s.proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"],
                }
            # Set cookies
            s.cookies.set(
                "__Secure-next-auth.session-token",
                self.config["session_token"],
            )
            # s.cookies.set("__Secure-next-auth.csrf-token", self.config['csrf_token'])
            response = s.get(
                "https://chat.openai.com/api/auth/session",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, "
                    "like Gecko) Version/16.1 Safari/605.1.15 ",
                },
            )
            try:
                self.config["session_token"] = response.cookies.get(
                    "__Secure-next-auth.session-token",
                )
                self.config["Authorization"] = response.json()["accessToken"]
                self.refresh_headers()
            except Exception as exc:
                print("Error refreshing session")
                self.debugger.log(response.text)
                raise Exception("Error refreshing session") from exc
        elif "email" in self.config and "password" in self.config:
            try:
                self.login(self.config["email"], self.config["password"])
            except Exception as exc:
                self.debugger.log("Login failed")
                raise exc
        elif "Authorization" in self.config:
            self.refresh_headers()
            return
        else:
            raise ValueError("No tokens provided")

    def login(self, email, password) -> None:
        self.debugger.log("Logging in...")
        use_proxy = False
        proxy = None
        if "proxy" in self.config:
            if self.config["proxy"] != "":
                use_proxy = True
                proxy = self.config["proxy"]
        auth = OpenAIAuth(email, password, use_proxy, proxy, debug=self.debug)
        try:
            auth.begin()
        except Exception as exc:
            # if ValueError with e as "Captcha detected" fail
            if exc == "Captcha detected":
                self.debugger.log(
                    "Captcha not supported. Use session tokens instead.")
                raise ValueError("Captcha detected") from exc
            raise exc
        if auth.access_token is not None:
            self.config["Authorization"] = auth.access_token
            if auth.session_token is not None:
                self.config["session_token"] = auth.session_token
            else:
                possible_tokens = auth.session.cookies.get(
                    "__Secure-next-auth.session-token",
                )
                if possible_tokens is not None:
                    if len(possible_tokens) > 1:
                        self.config["session_token"] = possible_tokens[0]
                    else:
                        try:
                            self.config["session_token"] = possible_tokens
                        except Exception as exc:
                            raise Exception("Error logging in") from exc
            self.refresh_headers()
        else:
            raise Exception("Error logging in")

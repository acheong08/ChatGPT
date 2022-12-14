# Author: @acheong08@fosstodon.org
# License: MIT
# Description: A Python wrapper for OpenAI's chatbot API
import json
import uuid
import asyncio

import httpx

import nest_asyncio

from typing import List

from playwright.async_api import async_playwright
from cf_clearance2 import async_cf_retry, async_stealth


def generate_uuid() -> str:
    """
    Generate a UUID for the session -- Internal use only

    :return: a random UUID
    :rtype: :obj:`str`
    """
    uid = str(uuid.uuid4())
    return uid


async def __async_func_for_check():
    pass


class Debugger:
    def __init__(self, debug: bool = False):
        if debug:
            print("Debugger enabled on OpenAIAuth")
        self.debug = debug

    def set_debug(self, debug: bool):
        self.debug = debug

    def log(self, message: str, end: str = "\n"):
        if self.debug:
            print(message, end=end)


class AsyncChatbot:
    """
    Initialize the AsyncChatbot.

    See wiki for the configuration json:
    https://github.com/acheong08/ChatGPT/wiki/Setup

    :param config: The configuration json
    :type config: :obj:`json`

    :param conversation_id: The conversation ID
    :type conversation_id: :obj:`str`, optional

    :param parent_id: The parent ID
    :type parent_id: :obj:`str`, optional

    :param debug: Whether to enable debug mode
    :type debug: :obj:`bool`, optional

    :param refresh: Whether to refresh the session
    :type refresh: :obj:`bool`, optional

    :param request_timeout: The network request timeout seconds
    :type request_timeout: :obj:`int`, optional

    :param base_url: The base url to chat.openai.com backend server,
        useful when set up a reverse proxy to avoid network issue.
    :type base_url: :obj:`str`, optional

    :return: The Chatbot object
    :rtype: :obj:`Chatbot`
    """
    config: json
    conversation_id: str
    parent_id: str
    base_url: str
    headers: dict
    conversation_id_prev_queue: List
    parent_id_prev_queue: List
    request_timeout: int
    captcha_solver: any

    def __init__(self, config, conversation_id=None, parent_id=None, debug=False, request_timeout=100,
                 captcha_solver=None, base_url="https://chat.openai.com/", max_rollbacks=20):
        self.debugger = Debugger(debug)
        self.debug = debug
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = parent_id if parent_id else generate_uuid()
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.captcha_solver = captcha_solver
        self.max_rollbacks = max_rollbacks
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        self.config["accept_language"] = 'en-US,en' if "accept_language" not in self.config.keys(
        ) else self.config["accept_language"]
        self.config["user_agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36" if "user_agent" not in self.config.keys(
        ) else self.config["user_agent"]
        self.headers = {
            "Accept": "text/event-stream",
            "Authorization": "Bearer ",
            "Content-Type": "application/json",
            "User-Agent": self.config["user_agent"],
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": self.config["accept_language"]+";q=0.9",
            "Referer": "https://chat.openai.com/chat",
        }
        self.refresh_session()

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = generate_uuid()

    def __refresh_headers(self) -> None:
        """
        Refresh the headers -- Internal use only

        :return: None
        """
        if not self.config.get("Authorization"):
            self.config["Authorization"] = ""
        self.headers["Authorization"] = "Bearer " + \
            self.config["Authorization"]
        self.headers["User-Agent"] = self.config["user_agent"]

    async def __get_chat_stream(self, data) -> None:
        """
        Generator for the chat stream -- Internal use only

        :param data: The data to send
        :type data: :obj:`dict`

        :return: None
        """
        s = httpx.AsyncClient()
        # Set cloudflare cookies
        if "cf_clearance" in self.config:
            s.cookies.set(
                "cf_clearance",
                self.config["cf_clearance"],
            )
        async with s.stream(
            'POST',
            self.base_url + "backend-api/conversation",
            headers=self.headers,
            data=json.dumps(data),
            timeout=self.request_timeout,
        ) as response:
            async for line in response.aiter_lines():
                try:
                    line = line[:-1]
                    if line == "" or line == "data: [DONE]":
                        continue
                    line = line[6:]
                    line = json.loads(line)
                    if len(line["message"]["content"]["parts"]) == 0:
                        continue
                    message = line["message"]["content"]["parts"][0]
                    self.conversation_id = line["conversation_id"]
                    self.parent_id = line["message"]["id"]
                    yield {
                        "message": message,
                        "conversation_id": self.conversation_id,
                        "parent_id": self.parent_id,
                    }
                except Exception as exc:
                    self.debugger.log(
                        f"Error when handling response, got values{line}")
                    raise Exception(
                        f"Error when handling response, got values{line}") from exc

    async def __get_chat_text(self, data) -> dict:
        """
        Get the chat response as text -- Internal use only
        :param data: The data to send
        :type data: :obj:`dict`
        :return: The chat response
        :rtype: :obj:`dict`
        """
        # Create request session
        async with httpx.AsyncClient() as s:
            # set headers
            s.headers = self.headers
            # Set cloudflare cookies
            if "cf_clearance" in self.config:
                s.cookies.set(
                    "cf_clearance",
                    self.config["cf_clearance"],
                )
            # Set proxies
            if self.config.get("proxy", "") != "":
                s.proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"],
                }
            response = await s.post(
                self.base_url + "backend-api/conversation",
                data=json.dumps(data),
                timeout=self.request_timeout,
            )
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except Exception as exc:
                self.debugger.log("Incorrect response from OpenAI API")
                raise Exception("Incorrect response from OpenAI API") from exc
            # Check if it is JSON
            if response.startswith("{"):
                response = json.loads(response)
                self.parent_id = response["message"]["id"]
                self.conversation_id = response["conversation_id"]
                message = response["message"]["content"]["parts"][0]
                return {
                    "message": message,
                    "conversation_id": self.conversation_id,
                    "parent_id": self.parent_id,
                }
            else:
                return None

    async def get_chat_response(self, prompt: str, output="text", conversation_id=None, parent_id=None) -> dict or None:
        """
        Get the chat response.

        :param prompt: The message sent to the chatbot
        :type prompt: :obj:`str`

        :param output: The output type `text` or `stream`
        :type output: :obj:`str`, optional

        :return: The chat response `{"message": "Returned messages", "conversation_id": "conversation ID", "parent_id": "parent ID"}` or None
        :rtype: :obj:`dict` or :obj:`None`
        """
        self.refresh_session(running_in_async=True)
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(generate_uuid()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id or self.conversation_id,
            "parent_message_id": parent_id or self.parent_id,
            "model": "text-davinci-002-render",
        }
        self.conversation_id_prev_queue.append(
            data["conversation_id"])  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
        while len(self.conversation_id_prev_queue) > self.max_rollbacks:  # LRU, remove oldest
            self.conversation_id_prev_queue.pop(0)
        while len(self.parent_id_prev_queue) > self.max_rollbacks:
            self.parent_id_prev_queue.pop(0)
        if output == "text":
            return await self.__get_chat_text(data)
        elif output == "stream":
            return self.__get_chat_stream(data)
        else:
            raise ValueError("Output must be either 'text' or 'stream'")

    def rollback_conversation(self, num=1) -> None:
        """
        Rollback the conversation.
        :param num: The number of messages to rollback
        :return: None
        """
        for i in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()

    def refresh_session(self, running_in_async=False) -> None:
        """
        Refresh the session.

        :return: None
        """
        if running_in_async:
            nest_asyncio.apply()
        # Either session_token, email and password or Authorization is required
        if not self.config.get("cf_clearance") or not self.config.get("session_token"):
            asyncio.run(self.get_cf_cookies())
        if self.config.get("session_token") and self.config.get("cf_clearance"):
            s = httpx.Client()
            if self.config.get("proxy"):
                s.proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"],
                }
            # Set cookies
            s.cookies.set(
                "__Secure-next-auth.session-token",
                self.config["session_token"],
            )

            s.cookies.set(
                "cf_clearance",
                self.config["cf_clearance"],
            )
            # s.cookies.set("__Secure-next-auth.csrf-token", self.config['csrf_token'])
            response = s.get(
                self.base_url + "api/auth/session",
                headers={
                    "User-Agent": self.config["user_agent"],
                },
            )
            # Check the response code
            if response.status_code != 200:
                if response.status_code == 403:
                    asyncio.run(self.get_cf_cookies())
                    self.refresh_session(running_in_async=running_in_async)
                    return
                else:
                    self.debugger.log(
                        f"Invalid status code: {response.status_code}")
                    raise Exception("Wrong response code")
            # Try to get new session token and Authorization
            try:
                if 'error' in response.json():
                    self.debugger.log("Error in response JSON")
                    self.debugger.log(response.json()['error'])
                    raise Exception
                self.config["session_token"] = response.cookies.get(
                    "__Secure-next-auth.session-token",
                )
                self.config["Authorization"] = response.json()["accessToken"]
                self.__refresh_headers()
            # If it fails, try to login with email and password to get tokens
            except Exception as exc:
                # Check if response JSON is empty
                if response.json() == {}:
                    self.debugger.log("Empty response")
                    self.debugger.log("Probably invalid session token")
                # Check if ['detail']['code'] == 'token_expired' in response JSON
                # First check if detail is in response JSON
                elif 'detail' in response.json():
                    # Check if code is in response JSON
                    if 'code' in response.json()['detail']:
                        # Check if code is token_expired
                        if response.json()['detail']['code'] == 'token_expired':
                            self.debugger.log("Token expired")
                raise Exception("Failed to refresh session") from exc
            return
        else:
            self.debugger.log(
                "No session_token, email and password or Authorization provided")
            raise ValueError(
                "No session_token, email and password or Authorization provided")

    async def get_cf_cookies(self) -> None:
        """
        Get cloudflare cookies.

        :return: None
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await async_stealth(page, pure=False)
            await page.goto('https://chat.openai.com/')
            page_wait_for_url = 'https://chat.openai.com/chat' if not self.config.get(
                'session_token') else None
            res = await async_cf_retry(
                page, wait_for_url=page_wait_for_url)
            if res:
                cookies = await page.context.cookies()
                for cookie in cookies:
                    if cookie.get('name') == 'cf_clearance':
                        cf_clearance_value = cookie.get('value')
                        self.debugger.log(cf_clearance_value)
                    elif cookie.get('name') == '__Secure-next-auth.session-token':
                        self.config['session_token'] = cookie.get('value')
                ua = await page.evaluate('() => {return navigator.userAgent}')
                self.debugger.log(ua)
            else:
                self.debugger.log("cf challenge fail")
                raise Exception("cf challenge fail")
            await browser.close()
            del browser
            self.config['cf_clearance'] = cf_clearance_value
            self.config['user_agent'] = ua

    def send_feedback(
        self,
        is_good: bool,
        is_harmful=False,
        is_not_true=False,
        is_not_helpful=False,
        description=None,
    ):
        from dataclasses import dataclass

        @ dataclass
        class ChatGPTTags:
            Harmful = "harmful"
            NotTrue = "false"
            NotHelpful = "not-helpful"

        url = self.base_url + "backend-api/conversation/message_feedback"

        data = {
            "conversation_id": self.conversation_id,
            "message_id": self.parent_id,
            "rating": "thumbsUp" if is_good else "thumbsDown",
        }

        if not is_good:
            tags = list()
            if is_harmful:
                tags.append(ChatGPTTags.Harmful)
            if is_not_true:
                tags.append(ChatGPTTags.NotTrue)
            if is_not_helpful:
                tags.append(ChatGPTTags.NotHelpful)
            data["tags"] = tags

        if description is not None:
            data["text"] = description

        response = httpx.post(
            url,
            headers=self.headers,
            data=json.dumps(data),
            timeout=self.request_timeout,
        )

        return response


class Chatbot(AsyncChatbot):
    """
    Initialize the Chatbot.

    See wiki for the configuration json:
    https://github.com/acheong08/ChatGPT/wiki/Setup

    :param config: The configuration json
    :type config: :obj:`json`

    :param conversation_id: The conversation ID
    :type conversation_id: :obj:`str`, optional

    :param parent_id: The parent ID
    :type parent_id: :obj:`str`, optional

    :param debug: Whether to enable debug mode
    :type debug: :obj:`bool`, optional

    :param refresh: Whether to refresh the session
    :type refresh: :obj:`bool`, optional

    :param request_timeout: The network request timeout seconds
    :type request_timeout: :obj:`int`, optional

    :param base_url: The base url to chat.openai.com backend server,
        useful when set up a reverse proxy to avoid network issue.
    :type base_url: :obj:`str`, optional

    :return: The Chatbot object
    :rtype: :obj:`Chatbot`
    """

    def __get_chat_stream(self, data) -> None:
        """
        Generator for the chat stream -- Internal use only

        :param data: The data to send
        :type data: :obj:`dict`

        :return: None
        """
        s = httpx.Client()
        # Set cloudflare cookies
        if "cf_clearance" in self.config:
            s.cookies.set(
                "cf_clearance",
                self.config["cf_clearance"],
            )
        with s.stream(
            'POST',
            self.base_url + "backend-api/conversation",
            headers=self.headers,
            data=json.dumps(data),
            timeout=self.request_timeout,
        ) as response:
            for line in response.iter_lines():
                try:
                    line = line[:-1]
                    if line == "" or line == "data: [DONE]":
                        continue
                    line = line[6:]
                    line = json.loads(line)
                    if len(line["message"]["content"]["parts"]) == 0:
                        continue
                    message = line["message"]["content"]["parts"][0]
                    self.conversation_id = line["conversation_id"]
                    self.parent_id = line["message"]["id"]
                    yield {
                        "message": message,
                        "conversation_id": self.conversation_id,
                        "parent_id": self.parent_id,
                    }
                except Exception as exc:
                    self.debugger.log(
                        f"Error when handling response, got values{line}")
                    raise Exception(
                        f"Error when handling response, got values{line}") from exc

    def get_chat_response(self, prompt: str, output="text", conversation_id=None, parent_id=None) -> dict or None:
        """
        Get the chat response.

        :param prompt: The message sent to the chatbot
        :type prompt: :obj:`str`

        :param output: The output type `text` or `stream`
        :type output: :obj:`str`, optional

        :return: The chat response `{"message": "Returned messages", "conversation_id": "conversation ID", "parent_id": "parent ID"}` or None
        :rtype: :obj:`dict` or :obj:`None`
        """
        try:
            # Check if running in nest use of asyncio.run()
            asyncio.run(self.__async_func_for_check())
        except RuntimeError:
            self.debugger.log("detect nest use of asyncio")
            nest_asyncio.apply()
        self.refresh_session()
        if output == "text":
            coroutine_object = super().get_chat_response(
                prompt, output, conversation_id, parent_id)
            return asyncio.run(coroutine_object)

        if output == "stream":
            data = {
                "action": "next",
                "messages": [
                    {
                        "id": str(generate_uuid()),
                        "role": "user",
                        "content": {"content_type": "text", "parts": [prompt]},
                    },
                ],
                "conversation_id": conversation_id or self.conversation_id,
                "parent_message_id": parent_id or self.parent_id,
                "model": "text-davinci-002-render",
            }
            self.conversation_id_prev_queue.append(
                data["conversation_id"])  # for rollback
            self.parent_id_prev_queue.append(data["parent_message_id"])
            return self.__get_chat_stream(data)

    async def __async_func_for_check(self):
        pass

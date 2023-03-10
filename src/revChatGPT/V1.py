"""
Standard ChatGPT
"""
from __future__ import annotations

import base64
import contextlib
import json
import logging
import os
import os.path as osp
import sys
import time
import uuid
from functools import wraps
from os import environ
from os import getenv
from typing import NoReturn

import requests
from httpx import AsyncClient
from OpenAIAuth import Authenticator
from OpenAIAuth import Error as AuthError

from .utils import create_completer
from .utils import create_session
from .utils import get_input

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
    )

log = logging.getLogger(__name__)


def logger(is_timed: bool):
    """Logger decorator

    Args:
        is_timed (bool): Whether to include function running time in exit log

    Returns:
        _type_: decorated function
    """

    def decorator(func):
        wraps(func)

        def wrapper(*args, **kwargs):
            log.debug(
                "Entering %s with args %s and kwargs %s",
                func.__name__,
                args,
                kwargs,
            )
            start = time.time()
            out = func(*args, **kwargs)
            end = time.time()
            if is_timed:
                log.debug(
                    "Exiting %s with return value %s. Took %s seconds.",
                    func.__name__,
                    out,
                    end - start,
                )
            else:
                log.debug("Exiting %s with return value %s", func.__name__, out)

            return out

        return wrapper

    return decorator


BASE_URL = environ.get("CHATGPT_BASE_URL") or "https://bypass.duti.tech/api/"


class ErrorType:
    # define consts for the error codes
    USER_ERROR = -1
    UNKNOWN_ERROR = 0
    SERVER_ERROR = 1
    RATE_LIMIT_ERROR = 2
    INVALID_REQUEST_ERROR = 3
    EXPIRED_ACCESS_TOKEN_ERROR = 4
    INVALID_ACCESS_TOKEN_ERROR = 5
    PROHIBITED_CONCURRENT_QUERY_ERROR = 6


class Error(Exception):
    """
    Base class for exceptions in this module.
    Error codes:
    -1: User error
    0: Unknown error
    1: Server error
    2: Rate limit error
    3: Invalid request error
    4: Expired access token error
    5: Invalid access token error
    6: Prohibited concurrent query error
    """

    source: str
    message: str
    code: int

    def __init__(self, source: str, message: str, code: int = 0) -> None:
        self.source = source
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"

    def __repr__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"


class colors:
    """
    Colors for printing
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self) -> None:
        if getenv("NO_COLOR"):
            self.HEADER = ""
            self.OKBLUE = ""
            self.OKCYAN = ""
            self.OKGREEN = ""
            self.WARNING = ""
            self.FAIL = ""
            self.ENDC = ""
            self.BOLD = ""
            self.UNDERLINE = ""


bcolors = colors()


class Chatbot:
    """
    Chatbot class for ChatGPT
    """

    @logger(is_timed=True)
    def __init__(
        self,
        config: dict[str, str],
        conversation_id: str | None = None,
        parent_id: str | None = None,
        session_client=None,
        lazy_loading: bool = False,
    ) -> None:
        """Initialize a chatbot

        Args:
            config (dict[str, str]): Login and proxy info. Example:
                {
                    "email": "OpenAI account email",
                    "password": "OpenAI account password",
                    "session_token": "<session_token>"
                    "access_token": "<access_token>"
                    "proxy": "<proxy_url_string>",
                    "paid": True/False, # whether this is a plus account
                }
                More details on these are available at https://github.com/acheong08/ChatGPT#configuration
            conversation_id (str | None, optional): Id of the conversation to continue on. Defaults to None.
            parent_id (str | None, optional): Id of the previous response message to continue on. Defaults to None.
            session_client (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
        """
        user_home = getenv("HOME")
        if user_home is None:
            self.cache_path = osp.join(os.getcwd(), ".chatgpt_cache.json")
        else:
            # mkdir ~/.config/revChatGPT
            if not osp.exists(osp.join(user_home, ".config")):
                os.mkdir(osp.join(user_home, ".config"))
            if not osp.exists(osp.join(user_home, ".config", "revChatGPT")):
                os.mkdir(osp.join(user_home, ".config", "revChatGPT"))
            self.cache_path = osp.join(user_home, ".config", "revChatGPT", "cache.json")

        self.config = config
        self.session = session_client() if session_client else requests.Session()
        try:
            cached_access_token = self.__get_cached_access_token(
                self.config.get("email", None),
            )
        except Error as error:
            if error.code == 5:
                raise error
            cached_access_token = None
        if cached_access_token is not None:
            self.config["access_token"] = cached_access_token

        if "proxy" in config:
            if not isinstance(config["proxy"], str):
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            if isinstance(self.session, AsyncClient):
                proxies = {
                    "http://": config["proxy"],
                    "https://": config["proxy"],
                }
                self.session = AsyncClient(proxies=proxies)
            else:
                self.session.proxies.update(proxies)
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        self.lazy_loading = lazy_loading

        self.__check_credentials()

    @logger(is_timed=True)
    def __check_credentials(self) -> None:
        """Check login info and perform login

        Any one of the following is sufficient for login. Multiple login info can be provided at the same time and they will be used in the order listed below.
            - access_token
            - session_token
            - email + password

        Raises:
            Exception: _description_
            AuthError: _description_
        """
        if "access_token" in self.config:
            self.__set_access_token(self.config["access_token"])
        elif "session_token" in self.config:
            pass
        elif "email" not in self.config or "password" not in self.config:
            raise Exception("Insufficient login details provided!")
        if "access_token" not in self.config:
            try:
                self.__login()
            except AuthError as error:
                raise error

    @logger(is_timed=False)
    def __set_access_token(self, access_token: str) -> None:
        """Set access token in request header and self.config, then cache it to file.

        Args:
            access_token (str): access_token
        """
        self.session.headers.clear()
        self.session.headers.update(
            {
                "Accept": "text/event-stream",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Openai-Assistant-App-Id": "",
                "Connection": "close",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://chat.openai.com/chat",
            },
        )
        self.session.cookies.update(
            {
                "library": "revChatGPT",
            },
        )

        self.config["access_token"] = access_token

        email = self.config.get("email", None)
        if email is not None:
            self.__cache_access_token(email, access_token)

    @logger(is_timed=False)
    def __get_cached_access_token(self, email: str | None) -> str | None:
        """Read access token from cache

        Args:
            email (str | None): email of the account to get access token

        Raises:
            Error: _description_
            Error: _description_
            Error: _description_

        Returns:
            str | None: access token string or None if not found
        """
        email = email or "default"
        cache = self.__read_cache()
        access_token = cache.get("access_tokens", {}).get(email, None)

        # Parse access_token as JWT
        if access_token is not None:
            try:
                # Split access_token into 3 parts
                s_access_token = access_token.split(".")
                # Add padding to the middle part
                s_access_token[1] += "=" * ((4 - len(s_access_token[1]) % 4) % 4)
                d_access_token = base64.b64decode(s_access_token[1])
                d_access_token = json.loads(d_access_token)
            except base64.binascii.Error:
                raise Error(
                    source="__get_cached_access_token",
                    message="Invalid access token",
                    code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                ) from None
            except json.JSONDecodeError:
                raise Error(
                    source="__get_cached_access_token",
                    message="Invalid access token",
                    code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                ) from None

            exp = d_access_token.get("exp", None)
            if exp is not None and exp < time.time():
                raise Error(
                    source="__get_cached_access_token",
                    message="Access token expired",
                    code=ErrorType.EXPIRED_ACCESS_TOKEN_ERROR,
                )

        return access_token

    @logger(is_timed=False)
    def __cache_access_token(self, email: str, access_token: str) -> None:
        """Write an access token to cache

        Args:
            email (str): account email
            access_token (str): account access token
        """
        email = email or "default"
        cache = self.__read_cache()
        if "access_tokens" not in cache:
            cache["access_tokens"] = {}
        cache["access_tokens"][email] = access_token
        self.__write_cache(cache)

    @logger(is_timed=False)
    def __write_cache(self, info: dict) -> None:
        """Write cache info to file

        Args:
            info (dict): cache info, current format
            {
                "access_tokens":{"someone@example.com": 'this account's access token', }
            }
        """
        dirname = osp.dirname(self.cache_path) or "."
        os.makedirs(dirname, exist_ok=True)
        json.dump(info, open(self.cache_path, "w", encoding="utf-8"), indent=4)

    @logger(is_timed=False)
    def __read_cache(self):
        try:
            cached = json.load(open(self.cache_path, encoding="utf-8"))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            cached = {}
        return cached

    @logger(is_timed=True)
    def __login(self) -> None:
        if (
            "email" not in self.config or "password" not in self.config
        ) and "session_token" not in self.config:
            log.error("Insufficient login details provided!")
            raise Exception("Insufficient login details provided!")
        auth = Authenticator(
            email_address=self.config.get("email"),
            password=self.config.get("password"),
            proxy=self.config.get("proxy"),
        )
        if self.config.get("session_token"):
            log.debug("Using session token")
            auth.session_token = self.config["session_token"]
            auth.get_access_token()
            if auth.access_token is None:
                del self.config["session_token"]
                self.__login()
                return
        else:
            log.debug("Using authenticator to get access token")
            auth.begin()
            self.config["session_token"] = auth.session_token
            auth.get_access_token()

        self.__set_access_token(auth.access_token)

    @logger(is_timed=True)
    def ask(
        self,
        prompt: str,
        conversation_id: str | None = None,
        parent_id: str | None = None,
        timeout: float = 360,
    ):
        """Ask a question to the chatbot
        Args:
            prompt (str): The question
            conversation_id (str | None, optional): UUID for the conversation to continue on. Defaults to None.
            parent_id (str | None, optional): UUID for the message to continue on. Defaults to None.
            timeout (float, optional): Timeout for getting the full response, unit is second. Defaults to 360.

        Raises:
            Error: _description_
            Exception: _description_
            Error: _description_
            Error: _description_
            Error: _description_

        Yields:
            _type_: _description_
        """

        if parent_id is not None and conversation_id is None:
            log.error("conversation_id must be set once parent_id is set")
            raise Error(
                source="User",
                message="conversation_id must be set once parent_id is set",
                code=ErrorType.USER_ERROR,
            )

        if conversation_id is not None and conversation_id != self.conversation_id:
            log.debug("Updating to new conversation by setting parent_id to None")
            self.parent_id = None

        conversation_id = conversation_id or self.conversation_id
        parent_id = parent_id or self.parent_id
        if conversation_id is None and parent_id is None:
            parent_id = str(uuid.uuid4())
            log.debug("New conversation, setting parent_id to new UUID4: %s", parent_id)

        if conversation_id is not None and parent_id is None:
            if conversation_id not in self.conversation_mapping:
                if self.lazy_loading:
                    log.debug(
                        "Conversation ID %s not found in conversation mapping, try to get conversation history for the given ID",
                        conversation_id,
                    )
                    with contextlib.suppress(Exception):
                        history = self.get_msg_history(conversation_id)
                        self.conversation_mapping[conversation_id] = history[
                            "current_node"
                        ]
                else:
                    log.debug(
                        "Conversation ID %s not found in conversation mapping, mapping conversations",
                        conversation_id,
                    )

                    self.__map_conversations()

            if conversation_id in self.conversation_mapping:
                log.debug(
                    "Conversation ID %s found in conversation mapping, setting parent_id to %s",
                    conversation_id,
                    self.conversation_mapping[conversation_id],
                )
                parent_id = self.conversation_mapping[conversation_id]
            else:  # invalid conversation_id provided, treat as a new conversation
                conversation_id = None
                parent_id = str(uuid.uuid4())
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id,
            "parent_message_id": parent_id,
            "model": "text-davinci-002-render-paid"
            if self.config.get("paid")
            else "text-davinci-002-render-sha",
        }
        log.debug("Sending the payload")
        log.debug(json.dumps(data, indent=2))

        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=f"{BASE_URL}conversation",
            data=json.dumps(data),
            timeout=timeout,
            stream=True,
        )
        self.__check_response(response)
        for line in response.iter_lines():
            # remove b' and ' at the beginning and end and ignore case
            line = str(line)[2:-1]
            if line.lower() == "internal server error":
                log.error("Internal Server Error: %s", line)
                raise Error(
                    source="ask",
                    message="Internal Server Error",
                    code=ErrorType.SERVER_ERROR,
                )
            if line == "" or line is None:
                continue
            if "data: " in line:
                line = line[6:]
            if line == "[DONE]":
                break

            line = line.replace('\\"', '"')
            line = line.replace("\\'", "'")
            line = line.replace("\\\\", "\\")

            try:
                line = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            if not self.__check_fields(line):
                log.error("Field missing", exc_info=True)
                line_detail = line.get("detail")
                if isinstance(line_detail, str):
                    if (
                        line_detail.lower()
                        == "too many requests in 1 hour. try again later."
                    ):
                        log.error("Rate limit exceeded")
                        raise Error(
                            source="ask",
                            message=line.get("detail"),
                            code=ErrorType.RATE_LIMIT_ERROR,
                        )
                    if line_detail.lower().startswith(
                        "only one message at a time.",
                    ):
                        log.error("Prohibited concurrent query")
                        raise Error(
                            source="ask",
                            message=line_detail,
                            code=ErrorType.PROHIBITED_CONCURRENT_QUERY_ERROR,
                        )
                    if line_detail.lower() == "invalid_api_key":
                        log.error("Invalid access token")
                        raise Error(
                            source="ask",
                            message=line_detail,
                            code=ErrorType.INVALID_REQUEST_ERROR,
                        )
                    if line_detail.lower() == "invalid_token":
                        log.error("Invalid access token")
                        raise Error(
                            source="ask",
                            message=line_detail,
                            code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                        )
                elif isinstance(line_detail, dict):
                    if line_detail.get("code") == "invalid_jwt":
                        log.error("Invalid access token")
                        raise Error(
                            source="ask",
                            message=line_detail.get("message", "invalid_jwt"),
                            code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                        )

                raise Error(
                    source="ask",
                    message="Field missing",
                    code=ErrorType.SERVER_ERROR,
                )
            message = line["message"]["content"]["parts"][0]
            if message == prompt:
                continue
            conversation_id = line["conversation_id"]
            parent_id = line["message"]["id"]
            try:
                model = line["message"]["metadata"]["model_slug"]
            except KeyError:
                model = None
            log.debug("Received message: %s", message)
            log.debug("Received conversation_id: %s", conversation_id)
            log.debug("Received parent_id: %s", parent_id)
            yield {
                "message": message,
                "conversation_id": conversation_id,
                "parent_id": parent_id,
                "model": model,
            }
        self.conversation_mapping[conversation_id] = parent_id
        if parent_id is not None:
            self.parent_id = parent_id
        if conversation_id is not None:
            self.conversation_id = conversation_id

    @logger(is_timed=False)
    def __check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except (TypeError, KeyError):
            return False
        return True

    @logger(is_timed=False)
    def __check_response(self, response: requests.Response) -> None:
        """Make sure response is success

        Args:
            response (_type_): _description_

        Raises:
            Error: _description_
        """
        if response.status_code != 200:
            print(response.text)
            raise Error(
                source="OpenAI",
                message=response.text,
                code=response.status_code,
            )

    @logger(is_timed=True)
    def get_conversations(
        self,
        offset: int = 0,
        limit: int = 20,
        encoding: str | None = None,
    ):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = f"{BASE_URL}conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.__check_response(response)
        if encoding is not None:
            response.encoding = encoding
        data = json.loads(response.text)
        return data["items"]

    @logger(is_timed=True)
    def get_msg_history(self, convo_id: str, encoding: str | None = None):
        """
        Get message history
        :param id: UUID of conversation
        :param encoding: String
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = self.session.get(url)
        self.__check_response(response)
        if encoding is not None:
            response.encoding = encoding
        return json.loads(response.text)

    @logger(is_timed=True)
    def gen_title(self, convo_id: str, message_id: str) -> None:
        """
        Generate title for conversation
        """
        response = self.session.post(
            f"{BASE_URL}conversation/gen_title/{convo_id}",
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        self.__check_response(response)

    @logger(is_timed=True)
    def change_title(self, convo_id: str, title: str) -> None:
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = self.session.patch(url, data=json.dumps({"title": title}))
        self.__check_response(response)

    @logger(is_timed=True)
    def delete_conversation(self, convo_id: str) -> None:
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    @logger(is_timed=True)
    def clear_conversations(self) -> None:
        """
        Delete all conversations
        """
        url = f"{BASE_URL}conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    @logger(is_timed=False)
    def __map_conversations(self) -> None:
        conversations = self.get_conversations()
        histories = [self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    @logger(is_timed=False)
    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    @logger(is_timed=False)
    def rollback_conversation(self, num: int = 1) -> None:
        """
        Rollback the conversation.
        :param num: Integer. The number of messages to rollback
        :return: None
        """
        for _ in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()


class AsyncChatbot(Chatbot):
    """
    Async Chatbot class for ChatGPT
    """

    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
    ) -> None:
        super().__init__(
            config=config,
            conversation_id=conversation_id,
            parent_id=parent_id,
            session_client=AsyncClient,
        )

    async def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        timeout=360,
    ):
        """
        Ask a question to the chatbot
        """
        if parent_id is not None and conversation_id is None:
            raise Error(
                source="User",
                message="conversation_id must be set once parent_id is set",
                code=ErrorType.SERVER_ERROR,
            )

        if conversation_id is not None and conversation_id != self.conversation_id:
            self.parent_id = None

        conversation_id = conversation_id or self.conversation_id
        parent_id = parent_id or self.parent_id
        if conversation_id is None and parent_id is None:
            parent_id = str(uuid.uuid4())

        if conversation_id is not None and parent_id is None:
            if conversation_id not in self.conversation_mapping:
                await self.__map_conversations()
            parent_id = self.conversation_mapping[conversation_id]
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id,
            "parent_message_id": parent_id,
            "model": "text-davinci-002-render-paid"
            if self.config.get("paid")
            else "text-davinci-002-render-sha",
        }

        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )
        self.parent_id_prev_queue.append(data["parent_message_id"])

        async with self.session.stream(
            method="POST",
            url=f"{BASE_URL}conversation",
            data=json.dumps(data),
            timeout=timeout,
        ) as response:
            self.__check_response(response)
            async for line in response.aiter_lines():
                if line == "" or line is None:
                    continue
                if "data: " in line:
                    line = line[6:]
                if "[DONE]" in line:
                    break

                try:
                    line = json.loads(line)
                except json.decoder.JSONDecodeError:
                    continue
                if not self.__check_fields(line):
                    raise Exception(f"Field missing. Details: {str(line)}")

                message = line["message"]["content"]["parts"][0]
                conversation_id = line["conversation_id"]
                parent_id = line["message"]["id"]
                model = (
                    line["message"]["metadata"]["model_slug"]
                    if "model_slug" in line["message"]["metadata"]
                    else None
                )
                yield {
                    "message": message,
                    "conversation_id": conversation_id,
                    "parent_id": parent_id,
                    "model": model,
                }
            self.conversation_mapping[conversation_id] = parent_id
            if parent_id is not None:
                self.parent_id = parent_id
            if conversation_id is not None:
                self.conversation_id = conversation_id

    async def get_conversations(self, offset=0, limit=20):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = f"{BASE_URL}conversations?offset={offset}&limit={limit}"
        response = await self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data["items"]

    async def get_msg_history(self, convo_id, encoding="utf-8"):
        """
        Get message history
        :param id: UUID of conversation
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = await self.session.get(url)
        if encoding is not None:
            response.encoding = encoding
            self.__check_response(response)
            return json.loads(response.text)

    async def gen_title(self, convo_id: str, message_id: str) -> None:
        """
        Generate title for conversation
        """
        url = f"{BASE_URL}conversation/gen_title/{convo_id}"
        response = await self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        await self.__check_response(response)

    async def change_title(self, convo_id: str, title: str) -> None:
        """
        Change title of conversation
        :param convo_id: UUID of conversation
        :param title: String
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = await self.session.patch(url, data=f'{{"title": "{title}"}}')
        self.__check_response(response)

    async def delete_conversation(self, convo_id: str) -> None:
        """
        Delete conversation
        :param convo_id: UUID of conversation
        """
        url = f"{BASE_URL}conversation/{convo_id}"
        response = await self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    async def clear_conversations(self) -> None:
        """
        Delete all conversations
        """
        url = f"{BASE_URL}conversations"
        response = await self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    async def __map_conversations(self) -> None:
        conversations = await self.get_conversations()
        histories = [await self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    def __check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except (TypeError, KeyError):
            return False
        return True

    def __check_response(self, response) -> None:
        response.raise_for_status()


get_input = logger(is_timed=False)(get_input)


@logger(is_timed=False)
def configure():
    """
    Looks for a config file in the following locations:
    """
    config_files = ["config.json"]
    if xdg_config_home := getenv("XDG_CONFIG_HOME"):
        config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
    if user_home := getenv("HOME"):
        config_files.append(f"{user_home}/.config/revChatGPT/config.json")

    if config_file := next((f for f in config_files if osp.exists(f)), None):
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("No config file found.")
        raise Exception("No config file found.")
    return config


@logger(is_timed=False)
def main(config: dict) -> NoReturn:
    """
    Main function for the chatGPT program.
    """
    chatbot = Chatbot(
        config,
        conversation_id=config.get("conversation_id"),
        parent_id=config.get("parent_id"),
    )

    def handle_commands(command: str) -> bool:
        if command == "!help":
            print(
                """
            !help - Show this message
            !reset - Forget the current conversation
            !config - Show the current configuration
            !rollback x - Rollback the conversation (x being the number of messages to rollback)
            !exit - Exit this program
            !setconversation - Changes the conversation
            """,
            )
        elif command == "!reset":
            chatbot.reset_chat()
            print("Chat session successfully reset.")
        elif command == "!config":
            print(json.dumps(chatbot.config, indent=4))
        elif command.startswith("!rollback"):
            try:
                rollback = int(command.split(" ")[1])
            except IndexError:
                logging.exception(
                    "No number specified, rolling back 1 message",
                    stack_info=True,
                )
                rollback = 1
            chatbot.rollback_conversation(rollback)
            print(f"Rolled back {rollback} messages.")
        elif command.startswith("!setconversation"):
            try:
                chatbot.conversation_id = chatbot.config[
                    "conversation_id"
                ] = command.split(" ")[1]
                print("Conversation has been changed")
            except IndexError:
                log.exception(
                    "Please include conversation UUID in command",
                    stack_info=True,
                )
                print("Please include conversation UUID in command")
        elif command == "!exit":
            sys.exit(0)
        else:
            return False
        return True

    session = create_session()
    completer = create_completer(
        ["!help", "!reset", "!config", "!rollback", "!exit", "!setconversation"],
    )
    print()
    try:
        while True:
            print(f"{bcolors.OKBLUE + bcolors.BOLD}You: {bcolors.ENDC}")

            prompt = get_input(session=session, completer=completer)
            if prompt.startswith("!") and handle_commands(prompt):
                continue

            print()
            print(f"{bcolors.OKGREEN + bcolors.BOLD}Chatbot: {bcolors.ENDC}")
            prev_text = ""
            for data in chatbot.ask(prompt):
                message = data["message"][len(prev_text) :]
                print(message, end="", flush=True)
                prev_text = data["message"]
            print(bcolors.ENDC)
            print()
    except (KeyboardInterrupt, EOFError):
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print(
        f"{bcolors.BOLD}{bcolors.WARNING}Press Esc followed by Enter or Alt+Enter to send a message.{bcolors.ENDC}",
    )
    main(configure())

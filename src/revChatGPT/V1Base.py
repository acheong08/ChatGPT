"""
 Base Class for Chatbot classes for ChatGPT
"""
import json
import logging
import time
import uuid
from functools import wraps
from os import environ
from os import getenv
from os.path import exists

import requests
from OpenAIAuth import Authenticator
from OpenAIAuth import Error as AuthError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
)

log = logging.getLogger(__name__)


def logger(is_timed):
    """
    Logger decorator
    """

    def decorator(func):
        wraps(func)

        def wrapper(*args, **kwargs):
            log.info(
                "Entering %s with args %s and kwargs %s",
                func.__name__,
                args,
                kwargs,
            )
            start = time.time()
            out = func(*args, **kwargs)
            end = time.time()
            if is_timed:
                log.info(
                    "Exiting %s with return value %s. Took %s seconds.",
                    func.__name__,
                    out,
                    end - start,
                )
            else:
                log.info("Exiting %s with return value %s", func.__name__, out)
            # Return the return value
            return out

        return wrapper

    return decorator


BASE_URL = environ.get("CHATGPT_BASE_URL") or "https://chatgpt.duti.tech/"


class Error(Exception):
    """Base class for exceptions in this module.
    # Error codes:
    # -1: User error
    # 0: Unknown error
    # 1: Server error
    # 2: Rate limit error
    # 3: Invalid request error
    """

    source: str
    message: str
    code: int

    def __init__(self, source: str = None, message: str = None, code: int = 0):
        self.source = source
        self.message = message
        self.code = code


class V1BaseClass:
    """
    Base Class for Chatbot classes for ChatGPT
    """

    @logger(is_timed=True)
    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
        session=None,
    ) -> None:
        self.config = config
        if session is not None:
            self.session = session
        else:
            self.session = requests.Session()

        if "proxy" in config:
            if isinstance(config["proxy"], str) is False:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            self.session.proxies.update(proxies)
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        if "email" in config and "password" in config:
            pass
        elif "access_token" in config:
            self.__refresh_headers(config["access_token"])
        elif "session_token" in config:
            pass
        else:
            raise Exception("No login details provided!")
        if "access_token" not in config:
            try:
                self.__login()
            except AuthError as error:
                raise error

    @logger(is_timed=False)
    def __refresh_headers(self, access_token):
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

    @logger(is_timed=True)
    def __login(self):
        if (
            "email" not in self.config or "password" not in self.config
        ) and "session_token" not in self.config:
            log.error("No login details provided!")
            raise Exception("No login details provided!")
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
            log.debug("Using authentiator to get access token")
            auth.begin()
            self.config["session_token"] = auth.session_token
            auth.get_access_token()

        self.__refresh_headers(auth.access_token)

    @logger(is_timed=False)
    def check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except TypeError:
            return False
        except KeyError:
            return False
        return True

    @logger(is_timed=False)
    def check_response(self, response):
        response.encoding = response.apparent_encoding
        if response.status_code != 200:
            print(response.text)
            error = Error()
            error.source = "OpenAI"
            error.code = response.status_code
            error.message = response.text
            raise error

    @logger(is_timed=False)
    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    @logger
    def rollback_conversation(self, num=1) -> None:
        """
        Rollback the conversation.
        :param num: The number of messages to rollback
        :return: None
        """
        for _ in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()


@logger(is_timed=False)
def get_input(prompt):
    """
    Multiline input function.
    """
    # Display the prompt
    print(prompt, end="")

    # Initialize an empty list to store the input lines
    lines = []

    # Read lines of input until the user enters an empty line
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    # Join the lines, separated by newlines, and store the result
    user_input = "\n".join(lines)

    # Return the input
    return user_input


@logger(is_timed=False)
def configure():
    """
    Looks for a config file in the following locations:
    """
    config_files = ["config.json"]
    xdg_config_home = getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
    user_home = getenv("HOME")
    if user_home:
        config_files.append(f"{user_home}/.config/revChatGPT/config.json")

    config_file = next((f for f in config_files if exists(f)), None)
    if config_file:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("No config file found.")
        raise Exception("No config file found.")
    return config

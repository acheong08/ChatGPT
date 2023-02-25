"""
Standard ChatGPT
"""
import asyncio
import json
import logging
import time
import uuid
from functools import wraps
from os import environ, getenv
from os.path import exists

import requests
from httpx import AsyncClient
from lib_openaiauth.src.OpenAIAuth import Authenticator
from lib_openaiauth.src.OpenAIAuth import Error as AuthError

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

            return out

        return wrapper

    return decorator


BASE_URL = environ.get("CHATGPT_BASE_URL") or "https://chatgpt.duti.tech/"


class Error(Exception):
    """Base class for exceptions in this module."""

    source: str
    message: str
    code: int

    def __init__(self, source: str = None, message: str = None, code: int = 0):
        self.source = source
        self.message = message
        self.code = code


class Chatbot:
    """
    Chatbot class for ChatGPT
    """

    @logger(is_timed=True)
    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
        session_client=None,
    ) -> None:
        self.config = config
        self.session = session_client() if session_client else requests.Session()

        if "proxy" in config:
            if isinstance(config["proxy"], str) is False:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            if isinstance(self.session, AsyncClient):
                self.session = AsyncClient(proxies=proxies)
            else:
                self.session.proxies.update(proxies)
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        self.auth = None

        self.__check_credentials()

    @logger(is_timed=True)
    def __check_credentials(self):
        if "email" in self.config and "password" in self.config:
            pass
        elif "access_token" in self.config:
            self.__refresh_headers(self.config["access_token"])
        elif "session_token" in self.config:
            pass
        else:
            raise Exception("No login details provided!")
        if "access_token" not in self.config:
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

        self.auth = auth
        self.__refresh_headers(auth.access_token)

    @logger(is_timed=True)
    def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        timeout=360,
    ):
        """
        Ask a question to the chatbot
        :param prompt: String
        :param conversation_id: UUID
        :param parent_id: UUID
        :param gen_title: Boolean
        """
        if parent_id is not None and conversation_id is None:
            log.error("conversation_id must be set once parent_id is set")
            error = Error()
            error.source = "User"
            error.message = "conversation_id must be set once parent_id is set"
            error.code = -1
            raise error

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

                log.debug(
                    "Conversation ID %s not found in conversation mapping, mapping conversations",
                    conversation_id,
                )

                self.__map_conversations()
            log.debug(
                "Conversation ID %s found in conversation mapping, setting parent_id to %s",
                conversation_id,
                self.conversation_mapping[conversation_id],
            )
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
            "model": "text-davinci-002-render-sha"
            if not self.config.get("paid")
            else "text-davinci-002-render-paid",
        }
        log.debug("Sending the payload")
        log.debug(json.dumps(data, indent=2))

        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=BASE_URL + "api/conversation",
            data=json.dumps(data),
            timeout=timeout,
            stream=True,
        )
        self.__check_response(response)
        for line in response.iter_lines():
            line = str(line)[2:-1]
            if line == "Internal Server Error":
                log.error("Internal Server Error: %s", line)
                raise Exception("Error: " + str(line))
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
                log.info("Error parsing JSON")
                continue
            if not self.__check_fields(line):
                log.error("Field missing", exc_info=True)
                if (
                    line.get("detail")
                    == "Too many requests in 1 hour. Try again later."
                ):
                    log.error("Rate limit exceeded")
                    raise Error(source="ask", message=line.get("detail"), code=2)
                raise Error(source="ask", message="Field missing", code=1)

            message = line["message"]["content"]["parts"][0]
            conversation_id = line["conversation_id"]
            parent_id = line["message"]["id"]
            log.debug("Received message: %s", message)
            log.debug("Received conversation_id: %s", conversation_id)
            log.debug("Received parent_id: %s", parent_id)
            yield {
                "message": message,
                "conversation_id": conversation_id,
                "parent_id": parent_id,
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
        except TypeError:
            return False
        except KeyError:
            return False
        return True

    @logger(is_timed=False)
    def __check_response(self, response):

        if response.status_code != 200:
            print(response.text)
            error = Error()
            error.source = "OpenAI"
            error.code = response.status_code
            error.message = response.text
            raise error

    @logger(is_timed=True)
    def get_conversations(self, offset=0, limit=20):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = BASE_URL + f"api/conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data["items"]

    @logger(is_timed=True)
    def get_msg_history(self, convo_id, encoding=None):
        """
        Get message history
        :param id: UUID of conversation
        :param encoding: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.get(url)
        self.__check_response(response)
        if encoding is not None:
            response.encoding = encoding
        data = json.loads(response.text)
        return data

    @logger(is_timed=True)
    def gen_title(self, convo_id, message_id):
        """
        Generate title for conversation
        """
        url = BASE_URL + f"api/conversation/gen_title/{convo_id}"
        response = self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        self.__check_response(response)

    @logger(is_timed=True)
    def change_title(self, convo_id, title):
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data=json.dumps({"title": title}))
        self.__check_response(response)

    @logger(is_timed=True)
    def delete_conversation(self, convo_id):
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    @logger(is_timed=True)
    def clear_conversations(self):
        """
        Delete all conversations
        """
        url = BASE_URL + "api/conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    @logger(is_timed=False)
    def __map_conversations(self):
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
            error = Error()
            error.source = "User"
            error.message = "conversation_id must be set once parent_id is set"
            error.code = -1
            raise error

        if conversation_id is not None and conversation_id != self.conversation_id:
            self.parent_id = None

        conversation_id = conversation_id or self.conversation_id
        parent_id = parent_id or self.parent_id
        if conversation_id is None and parent_id is None:
            parent_id = str(uuid.uuid4())

        if conversation_id is not None and parent_id is None:
            if conversation_id not in self.conversation_mapping:
                self.__map_conversations()
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
            "model": "text-davinci-002-render-sha"
            if not self.config.get("paid")
            else "text-davinci-002-render-paid",
        }

        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )
        self.parent_id_prev_queue.append(data["parent_message_id"])

        async with self.session.stream(
            method="POST",
            url=BASE_URL + "api/conversation",
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

                line = (
                    line.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
                )

                try:
                    line = json.loads(line)
                except json.decoder.JSONDecodeError:
                    continue
                if not self.__check_fields(line):
                    raise Exception("Field missing. Details: " + str(line))

                message = line["message"]["content"]["parts"][0]
                conversation_id = line["conversation_id"]
                parent_id = line["message"]["id"]
                yield {
                    "message": message,
                    "conversation_id": conversation_id,
                    "parent_id": parent_id,
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
        url = BASE_URL + f"api/conversations?offset={offset}&limit={limit}"
        response = await self.session.get(url)
        await self.__check_response(response)
        data = json.loads(await response.text())
        return data["items"]

    async def get_msg_history(self, convo_id, encoding="utf-8"):
        """
        Get message history
        :param id: UUID of conversation
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = await self.session.get(url)
        if encoding is not None:
            response.encoding = encoding
            await self.__check_response(response)
            data = json.loads(await response.text())
            return data

    async def gen_title(self, convo_id, message_id):
        """
        Generate title for conversation
        """
        url = BASE_URL + f"api/conversation/gen_title/{convo_id}"
        response = await self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        await self.__check_response(response)

    async def change_title(self, convo_id, title):
        """
        Change title of conversation
        :param convo_id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = await self.session.patch(url, data=f'{{"title": "{title}"}}')
        self.__check_response(response)

    async def delete_conversation(self, convo_id):
        """
        Delete conversation
        :param convo_id: UUID of conversation
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = await self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    async def clear_conversations(self):
        """
        Delete all conversations
        """
        url = BASE_URL + "api/conversations"
        response = await self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    async def __map_conversations(self):
        conversations = await self.get_conversations()
        histories = [await self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    def __check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except TypeError:
            return False
        except KeyError:
            return False
        return True

    def __check_response(self, response):
        response.raise_for_status()


@logger(is_timed=False)
def get_input(prompt):
    """
    Multiline input function.
    """

    print(prompt, end="")

    lines = []

    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    user_input = "\n".join(lines)

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


@logger(is_timed=False)
def main(config: dict):
    """
    Main function for the chatGPT program.
    """
    print("Logging in...")
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
            exit(0)
        else:
            return False
        return True

    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if handle_commands(prompt):
                continue

        print("Chatbot: ")
        prev_text = ""
        for data in chatbot.ask(
            prompt,
        ):
            message = data["message"][len(prev_text) :]
            print(message, end="", flush=True)
            prev_text = data["message"]
        print()


if __name__ == "__main__":
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    main(configure())

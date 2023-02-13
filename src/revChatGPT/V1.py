"""
Standard ChatGPT
"""
import json
import logging
import sys
import uuid
from os import environ
from os import getenv
from os.path import exists

import requests
from OpenAIAuth.OpenAIAuth import OpenAIAuth

# Disable all logging
logging.basicConfig(level=logging.ERROR)

BASE_URL = environ.get("CHATGPT_BASE_URL") or "https://chatgpt.duti.tech/"


class Error(Exception):
    """Base class for exceptions in this module."""

    source: str
    message: str
    code: int


class Chatbot:
    """
    Chatbot class for ChatGPT
    """

    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
    ) -> None:
        self.config = config
        self.session = requests.Session()
        if "proxy" in config:
            if isinstance(config["proxy"], str) is False:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            self.session.proxies.update(proxies)
        if "verbose" in config:
            if type(config["verbose"]) != bool:
                raise Exception("Verbose must be a boolean!")
            self.verbose = config["verbose"]
        else:
            self.verbose = False
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        if "email" not in config:
            raise Exception("Email not found in config!")
        if "password" not in config:
            raise Exception("Password not found in config!")
        self.__login()

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

    def __login(self):
        auth = OpenAIAuth(
            email_address=self.config.get("email"),
            password=self.config.get("password"),
            proxy=self.config.get("proxy"),
        )
        auth.begin()
        access_token = auth.get_access_token()
        self.__refresh_headers(access_token)

    def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        # gen_title=True,
    ):
        """
        Ask a question to the chatbot
        :param prompt: String
        :param conversation_id: UUID
        :param parent_id: UUID
        :param gen_title: Boolean
        """
        if conversation_id is not None and parent_id is None:
            self.__map_conversations()
        if conversation_id is None:
            conversation_id = self.conversation_id
        if parent_id is None:
            parent_id = (
                self.parent_id
                if conversation_id == self.conversation_id
                else self.conversation_mapping[conversation_id]
            )
        # new_conv = conversation_id is None
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
            "parent_message_id": parent_id or str(uuid.uuid4()),
            "model": "text-davinci-002-render"
            if not self.config.get("paid")
            else "text-davinci-002-render-paid",
        }
        # new_conv = data["conversation_id"] is None
        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=BASE_URL + "backend-api/conversation",
            data=json.dumps(data),
            timeout=360,
            stream=True,
        )
        self.__check_response(response)

        compounded_resp = ""

        for line in response.iter_lines():
            line = str(line)[2:-1]
            if line == "" or line is None:
                continue
            if "data: " in line:
                line = line[6:]
            if line == "[DONE]":
                break
            # Try parse JSON
            try:
                line = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            if not self.__check_fields(line):
                continue
            message = line["message"]["content"]["parts"][0][len(compounded_resp) :]
            compounded_resp += message
            conversation_id = line["conversation_id"]
            parent_id = line["message"]["id"]
            yield {
                "message": message,
                "conversation_id": conversation_id,
                "parent_id": parent_id,
            }
        # if gen_title and new_conv:
        #     self.__gen_title(
        #         self.conversation_id,
        #         parent_id,
        #     )

    def __check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except TypeError:
            return False
        except KeyError:
            return False
        return True

    def __check_response(self, response):
        if response.status_code != 200:
            print(response.text)
            error = Error()
            error.source = "OpenAI"
            error.code = response.status_code
            error.message = response.text
            raise error

    def get_conversations(self, offset=0, limit=20):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = BASE_URL + f"backend-api/conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data["items"]

    def get_msg_history(self, convo_id):
        """
        Get message history
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{convo_id}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data

    # def __gen_title(self, convo_id, message_id):
    #     """
    #     Generate title for conversation
    #     """
    #     url = BASE_URL + f"backend-api/conversation/gen_title/{convo_id}"
    #     response = self.session.post(
    #         url,
    #         data=json.dumps(
    #             {"message_id": message_id, "model": "text-davinci-002-render"},
    #         ),
    #     )
    #     self.__check_response(response)

    def change_title(self, convo_id, title):
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"backend-api/conversation/{convo_id}"
        response = self.session.patch(url, data=f'{{"title": "{title}"}}')
        self.__check_response(response)

    def delete_conversation(self, convo_id):
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{convo_id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def clear_conversations(self):
        """
        Delete all conversations
        """
        url = BASE_URL + "backend-api/conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def __map_conversations(self):
        conversations = self.get_conversations()
        histories = [self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    def rollback_conversation(self, num=1) -> None:
        """
        Rollback the conversation.
        :param num: The number of messages to rollback
        :return: None
        """
        for _ in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()


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


def main(config):
    """
    Main function for the chatGPT program.
    """
    print("Logging in...")
    chatbot = Chatbot(config)
    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if prompt == "!help":
                print(
                    """
                !help - Show this message
                !reset - Forget the current conversation
                !config - Show the current configuration
                !rollback x - Rollback the conversation (x being the number of messages to rollback)
                !exit - Exit this program
                """,
                )
                continue
            elif prompt == "!reset":
                chatbot.reset_chat()
                print("Chat session successfully reset.")
                continue
            elif prompt == "!config":
                print(json.dumps(chatbot.config, indent=4))
                continue
            elif prompt.startswith("!rollback"):
                # Default to 1 rollback if no number is specified
                try:
                    rollback = int(prompt.split(" ")[1])
                except IndexError:
                    rollback = 1
                chatbot.rollback_conversation(rollback)
                print(f"Rolled back {rollback} messages.")
                continue
            elif prompt.startswith("!setconversation"):
                try:
                    chatbot.config["conversation"] = prompt.split(" ")[1]
                    print("Conversation has been changed")
                except IndexError:
                    print("Please include conversation UUID in command")
                continue
            elif prompt == "!exit":
                break
        print("Chatbot: ")
        for data in chatbot.ask(
            prompt,
            conversation_id=chatbot.config.get("conversation"),
            parent_id=chatbot.config.get("parent_id"),
        ):
            print(data["message"], end="")
            sys.stdout.flush()
        print()
        # print(message["message"])


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

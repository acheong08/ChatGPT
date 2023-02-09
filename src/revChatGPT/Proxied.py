import json
import logging
import uuid
from os import environ

from OpenAIAuth.OpenAIAuth import OpenAIAuth

import tls_client

# Disable all logging
logging.basicConfig(level=logging.ERROR)

BASE_URL = environ.get("CHATGPT_BASE_URL") or "http://127.0.0.1:5000/"

class Chatbot:
    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
    ) -> None:
        self.config = config
        self.session = tls_client.Session(
            client_identifier="chrome_108",
        )
        if "proxy" in config:
            if type(config["proxy"]) != str:
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
        auth = OpenAIAuth(email_address=self.config.get("email"), password=self.config.get("password"), proxy=self.config.get("proxy"))
        auth.begin()
        access_token = auth.get_access_token()
        self.__refresh_headers(access_token)

    def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        gen_title=False,
    ):
        """
        Ask a question to the chatbot
        :param prompt: String
        :param conversation_id: UUID
        :param parent_id: UUID
        :param gen_title: Boolean
        """
        self.__map_conversations()
        if conversation_id is None:
            conversation_id = self.conversation_id
        if parent_id is None:
            parent_id = (
                self.parent_id
                if conversation_id == self.conversation_id
                else self.conversation_mapping[conversation_id]
            )
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
            "model": "text-davinci-002-render",
        }
        new_conv = data["conversation_id"] is None
        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=BASE_URL + "backend-api/conversation",
            data=json.dumps(data),
            timeout_seconds=180,
        )
        if response.status_code != 200:
            print(response.text)
            raise Exception(
                f"Wrong response code: {response.status_code}! Refreshing session...",
            )
        else:
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except Exception as exc:
                print("Incorrect response from OpenAI API")
                raise Exception("Incorrect response from OpenAI API") from exc
            # Check if it is JSON
            if response.startswith("{"):
                response = json.loads(response)
                self.parent_id = response["message"]["id"]
                self.conversation_id = response["conversation_id"]
                message = response["message"]["content"]["parts"][0]
                res = {
                    "message": message,
                    "conversation_id": self.conversation_id,
                    "parent_id": self.parent_id,
                }
                if gen_title and new_conv:
                    try:
                        title = self.__gen_title(
                            self.conversation_id,
                            self.parent_id,
                        )["title"]
                    except Exception as exc:
                        split = prompt.split(" ")
                        title = " ".join(split[:3]) + ("..." if len(split) > 3 else "")
                    res["title"] = title
                return res
            else:
                return None

    def __check_response(self, response):
        if response.status_code != 200:
            print(response.text)
            raise Exception("Response code error: ", response.status_code)

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

    def get_msg_history(self, id):
        """
        Get message history
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data

    def __gen_title(self, id, message_id):
        """
        Generate title for conversation
        """
        url = BASE_URL + f"backend-api/conversation/gen_title/{id}"
        response = self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        self.__check_response(response)
        data = json.loads(response.text)
        return data

    def change_title(self, id, title):
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
        response = self.session.patch(url, data=f'{{"title": "{title}"}}')
        self.__check_response(response)

    def delete_conversation(self, id):
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
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
        for i in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()


def get_input(prompt):
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


from os import getenv
from os.path import exists


def configure():
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


def chatGPT_main(config):
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
                !refresh - Refresh the session authentication
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
            elif prompt == "!refresh":
                chatbot.__refresh_session()
                print("Session successfully refreshed.\n")
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
        try:
            print("Chatbot: ")
            message = chatbot.ask(
                prompt,
                conversation_id=chatbot.config.get("conversation"),
                parent_id=chatbot.config.get("parent_id"),
            )
            print(message["message"])
        except Exception as exc:
            print("Something went wrong!")
            print(exc)
            continue


def main():
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    chatGPT_main(configure())


if __name__ == "__main__":
    main()

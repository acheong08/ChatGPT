"""
Official API for ChatGPT
"""
import asyncio
import json
import os
import sys

import httpx
import tiktoken

from .utils import create_completer
from .utils import create_session
from .utils import get_input_async

ENCODER = tiktoken.get_encoding("gpt2")


def get_max_tokens(prompt: str) -> int:
    """
    Get the max tokens for a prompt
    """
    return 4000 - len(ENCODER.encode(prompt))


class Message:
    """
    A single exchange between the user and the bot
    """

    def __init__(self, text: str, author: str) -> None:
        self.text: str = text
        self.author: str = author


class Conversation:
    """
    A single conversation
    """

    def __init__(self) -> None:
        self.messages: list[Message] = []


CONVERSATION_BUFFER: int = int(os.environ.get("CONVERSATION_BUFFER") or 1500)


class Conversations:
    """
    Conversation handler
    """

    def __init__(self) -> None:
        self.conversations: dict[str][Conversation] = {}

    def add_message(self, message: Message, conversation_id: str) -> None:
        """
        Adds a message to a conversation
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation()
        self.conversations[conversation_id].messages.append(message)

    def get(self, conversation_id: str) -> str:
        """
        Builds a conversation string from a conversation id
        """
        if conversation_id not in self.conversations:
            return ""
        conversation = "".join(
            f"{message.author}: {message.text}<|im_sep|>\n\n"
            for message in self.conversations[conversation_id].messages
        )
        if len(ENCODER.encode(conversation)) > 4000 - CONVERSATION_BUFFER:
            self.purge_history(conversation_id)
            return self.get(conversation_id)
        return conversation

    def purge_history(self, conversation_id: str, num: int = 1) -> None:
        """
        Remove oldest messages from a conversation
        """
        if conversation_id not in self.conversations:
            return
        self.conversations[conversation_id].messages = self.conversations[
            conversation_id
        ].messages[num:]

    def rollback(self, conversation_id: str, num: int = 1) -> None:
        """
        Remove latest messages from a conversation
        """
        if conversation_id not in self.conversations:
            return
        self.conversations[conversation_id].messages = self.conversations[
            conversation_id
        ].messages[:-num]

    def remove(self, conversation_id: str) -> None:
        """
        Removes a conversation
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]


BASE_PROMPT = (
    os.environ.get("BASE_PROMPT")
    or """You are ChatGPT, a large language model by OpenAI. Respond conversationally\n\n\n"""
)

PROXY_URL = os.environ.get("PROXY_URL") or "https://pawan.duti.tech/api"


class Chatbot:
    """
    Handles everything seamlessly
    """

    def __init__(
        self,
        api_key: str,
        proxy=None,
    ) -> None:
        self.proxy = proxy
        self.api_key: str = api_key
        self.conversations = Conversations()
        self.login(api_key=api_key)

    async def ask(self, prompt: str, conversation_id: str = None) -> dict:
        """
        Gets a response from the API
        """
        if conversation_id is None:
            conversation_id = "default"
        self.conversations.add_message(
            Message(prompt, "User"),
            conversation_id=conversation_id,
        )
        conversation: str = self.conversations.get(conversation_id)
        # Build request body
        body = self.__get_config()
        body["prompt"] = BASE_PROMPT + conversation + "ChatGPT: "
        body["max_tokens"] = get_max_tokens(conversation)
        async with httpx.AsyncClient(proxies=self.proxy or None).stream(
            method="POST",
            url=f"{PROXY_URL}/completions",
            json=body,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=1080,
        ) as response:
            full_result = ""
            async for line in response.aiter_lines():
                if response.status_code == 429:
                    print("error: " + "Too many requests")
                    raise Exception("Too many requests")
                if response.status_code == 523:
                    print(
                        "error: "
                        + "Origin is unreachable. Ensure that you are authenticated and are using the correct pricing model.",
                    )
                    raise Exception(
                        "Origin is unreachable. Ensure that you are authenticated and are using the correct pricing model.",
                    )
                if response.status_code == 503:
                    print("error: " + "OpenAI error!")
                    raise Exception("OpenAI error!")
                if response.status_code != 200:
                    print(response.status_code)
                    print(line)
                    # raise Exception("Unknown error")
                    continue
                line = line.strip()
                if line in ["\n", ""]:
                    continue
                if line == "data: [DONE]":
                    break
                try:
                    # Remove "data: " from the start of the line
                    data = json.loads(line[6:])
                    if data is None:
                        continue
                    full_result += data["choices"][0]["text"].replace("<|im_end|>", "")
                    if "choices" not in data:
                        continue
                    yield data
                except json.JSONDecodeError:
                    continue
            self.conversations.add_message(
                Message(full_result, "ChatGPT"),
                conversation_id=conversation_id,
            )

    def __get_config(self) -> dict:
        return {
            "prompt": "Who are you?",
            "temperature": 0.7,
            "max_tokens": 256,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "model": "text-davinci-003",
            "stop": "<|im_end|>",
            "stream": True,
        }

    def login(self, api_key: str) -> None:
        """
        Login to the API
        """
        self.api_key = api_key


async def main() -> None:
    """
    Testing main function
    """
    import argparse

    print(
        """
        FreeGPT: A way to use OpenAI's GPT-3 API for free
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--proxy",
        help="Use a proxy",
        required=False,
        type=str,
        default=None,
    )
    parser.add_argument(
        "--api_key",
        help="OpenAI API key",
        required=False,
        default="pk-TNkDYMHpJKKuSfiAWJlUCKQSnKluoZxvLGKRPnPzxCDPdVxs",
    )
    args = parser.parse_args()
    print("Logging in...")
    chatbot = Chatbot(
        proxy=args.proxy,
        api_key=args.api_key,
    )
    print("Logged in\n")

    print("Type '!help' to show a full list of commands")
    print("Press Esc followed by Enter or Alt+Enter to send a message.\n")

    def commands(command: str) -> bool:
        if command == "!help":
            print(
                """
            !help - Show this help message
            !reset - Clear the current conversation
            !rollback <int> - Remove the latest <int> messages from the conversation
            !exit - Exit the program
            """,
            )
        elif command == "!reset":
            chatbot.conversations.remove("default")
            print("Conversation cleared")
        elif command.startswith("!rollback"):
            try:
                num = int(command.split(" ")[1])
                chatbot.conversations.rollback("default", num)
                print(f"Removed {num} messages from the conversation")
            except IndexError:
                print("Please specify the number of messages to remove")
            except ValueError:
                print("Please specify a valid number of messages to remove")
        elif command == "!exit":
            print("Exiting...")
            sys.exit(0)
        else:
            return False
        return True

    try:
        session = create_session()
        completer = create_completer(["!help", "!reset", "!rollback", "!exit"])
        while True:
            print()
            print("You:")
            prompt = await get_input_async(session=session, completer=completer)
            print()

            if prompt.startswith("!") and commands(prompt):
                continue

            print("ChatGPT:")
            async for line in chatbot.ask(prompt=prompt):
                result = line["choices"][0]["text"].replace("<|im_end|>", "")
                print(result, end="")
                sys.stdout.flush()
            print()
            print()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    # RUn main
    asyncio.run(main())

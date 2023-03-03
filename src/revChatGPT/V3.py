"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys

import requests
import tiktoken

from .utils import create_session
from .utils import get_input


ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"
ENCODER = tiktoken.get_encoding("gpt2")


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(
        self,
        api_key: str,
        engine: str = None,
        proxy: str = None,
        max_tokens: int = 3000,
        system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
    ) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        self.engine = engine or ENGINE
        self.session = requests.Session()
        self.api_key = api_key
        self.proxy = proxy
        self.conversation: list = [
            {
                "role": "system",
                "content": system_prompt,
            },
        ]
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens

        initial_conversation = "\n".join([x["content"] for x in self.conversation])
        if len(ENCODER.encode(initial_conversation)) > self.max_tokens:
            raise Exception("System prompt is too long")

    def __add_to_conversation(self, message: str, role: str):
        """
        Add a message to the conversation
        """
        self.conversation.append({"role": role, "content": message})

    def __truncate_conversation(self):
        """
        Truncate the conversation
        """
        while True:
            full_conversation = "\n".join([x["content"] for x in self.conversation])
            if (
                len(ENCODER.encode(full_conversation)) > self.max_tokens
                and len(self.conversation) > 1
            ):
                # Don't remove the first message
                self.conversation.pop(1)
            else:
                break

    def ask_stream(self, prompt: str, role: str = "user", **kwargs) -> str:
        """
        Ask a question
        """
        api_key = kwargs.get("api_key")
        self.__add_to_conversation(prompt, "user")
        self.__truncate_conversation()
        # Get response
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + (api_key or self.api_key)},
            json={
                "model": self.engine,
                "messages": self.conversation,
                "stream": True,
                # kwargs
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1),
                "n": kwargs.get("n", 1),
                "user": role,
            },
            stream=True,
        )
        if response.status_code != 200:
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        response_role: str = None
        full_response: str = ""
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue
            if "role" in delta:
                response_role = delta["role"]
            if "content" in delta:
                content = delta["content"]
                full_response += content
                yield content
        self.__add_to_conversation(full_response, response_role)

    def ask(self, prompt: str, role: str = "user", **kwargs):
        """
        Non-streaming ask
        """
        response = self.ask_stream(prompt, role, **kwargs)
        full_response: str = ""
        for chunk in response:
            full_response += chunk
        return full_response

    def rollback(self, n: int = 1):
        """
        Rollback the conversation
        """
        for _ in range(n):
            self.conversation.pop()

    def reset(self):
        """
        Reset the conversation
        """
        self.conversation = [
            {"role": "system", "content": self.system_prompt},
        ]

    def save(self, file: str):
        """
        Save the conversation to a JSON file
        """
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.conversation, f, indent=2)
        except FileNotFoundError:
            print(f"Error: {file} cannot be created")

    def load(self, file: str):
        """
        Load the conversation from a JSON  file
        """
        try:
            with open(file, "r", encoding="utf-8") as f:
                self.conversation = json.load(f)
        except FileNotFoundError:
            print(f"Error: {file} does not exist")


def main():
    """
    Main function
    """
    print(
        """
    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT
    """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press Esc followed by Enter or Alt+Enter to send a message.\n")

    def chatbot_commands(cmd: str) -> bool:
        """
        Handle chatbot commands
        """
        if cmd == "!help":
            print(
                """
            !help - Display this message
            !rollback n - Rollback the conversation by n messages
            !save filename - Save the conversation to a file
            !load filename - Load the conversation from a file
            !reset - Reset the conversation
            !exit - Quit chat
            """,
            )
        elif cmd == "!exit":
            exit()
        elif cmd == "!reset":
            chatbot.reset()
        else:
            _, *value = cmd.split(" ")
            if len(value) < 1:
                print("Invalid number of arguments")
                return False
            if cmd.startswith("!rollback"):
                chatbot.rollback(int(value[0]))
                print(f"\nRolled back by {value[0]} messages")
            elif cmd.startswith("!save"):
                chatbot.save(value[0])
                print(f"\nConversation has been saved to {value[0]}")
            elif cmd.startswith("!load"):
                chatbot.load(value[0])
                print(f"\n{len(chatbot.conversation)} messages loaded from {value[0]}")
            else:
                return False
        return True

    # Get API key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for response",
    )
    parser.add_argument(
        "--no_stream",
        action="store_true",
        help="Disable streaming",
    )
    parser.add_argument(
        "--base_prompt",
        type=str,
        default="You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
        help="Base prompt for chatbot",
    )
    args = parser.parse_args()
    # Initialize chatbot
    chatbot = Chatbot(api_key=args.api_key, system_prompt=args.base_prompt)
    session = create_session()
    # Start chat
    while True:
        print()
        try:
            print("User: ")
            prompt = get_input(session=session)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!"):
            if chatbot_commands(prompt):
                continue
        print()
        print("ChatGPT: ", flush=True)
        if args.no_stream:
            print(chatbot.ask(prompt, "user", temperature=args.temperature))
        else:
            for response in chatbot.ask_stream(prompt, temperature=args.temperature):
                print(response, end="", flush=True)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

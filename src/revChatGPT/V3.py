"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys
from datetime import date
import requests

import tiktoken

ENGINE = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo"

ENCODER = tiktoken.get_encoding("gpt2")


def get_max_tokens(prompt: str) -> int:
    """
    Get the max tokens for a prompt
    """
    return 4000 - len(ENCODER.encode(prompt))


def remove_suffix(input_string, suffix):
    """
    Remove suffix from string (Support for Python 3.8)
    """
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]
    return input_string


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(
        self,
        api_key: str,
        engine: str = None,
        proxy: str = None,
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
                "content": "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
            }
        ]

    def __add_to_conversation(self, message: str, role: str):
        """
        Add a message to the conversation
        """
        self.conversation.append({"role": role, "content": message})

    def ask_stream(self, prompt: str, role: str = "user", **kwargs) -> str:
        """
        Ask a question
        """
        self.__add_to_conversation(prompt, role)
        # Get response
        response = self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + self.api_key},
            json={
                "model": self.engine,
                "messages": self.conversation,
                "stream": True,
                # kwargs
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1),
                "n": kwargs.get("n", 1),
                "user": kwargs.get("user", "user"),
            },
            stream=True,
        )
        if response.status_code != 200:
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}"
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


def main():
    print(
        """
    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT
    """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")

    def get_input(prompt):
        """
        Multi-line input function
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

    def chatbot_commands(cmd: str) -> bool:
        """
        Handle chatbot commands
        """
        if cmd == "!help":
            print(
                """
            !help - Display this message
            !exit - Quit chat
            """,
            )
        elif cmd == "!exit":
            exit()
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
    args = parser.parse_args()
    # Initialize chatbot
    chatbot = Chatbot(api_key=args.api_key)
    # Start chat
    while True:
        try:
            prompt = get_input("\nUser:\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!"):
            if chatbot_commands(prompt):
                continue
        print("ChatGPT: ", flush=True)
        for response in chatbot.ask_stream(prompt, temperature=args.temperature):
            print(response, end="", flush=True)
        print()


if __name__ == "__main__":
    main()

"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys
from datetime import date

import openai
import tiktoken

ENGINE = os.environ.get("GPT_ENGINE") or "text-chat-davinci-002-20221122"

ENCODER = tiktoken.get_encoding("gpt2")


def get_max_tokens(prompt: str) -> int:
    """
    Get the max tokens for a prompt
    """
    return 4000 - len(ENCODER.encode(prompt))


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(self, api_key: str, buffer: int = None) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.conversations = Conversation()
        self.prompt = Prompt(buffer=buffer)

    def _get_completion(
        self,
        prompt: str,
        temperature: float = 0.5,
        stream: bool = False,
    ):
        """
        Get the completion function
        """
        return openai.Completion.create(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=stream,
        )

    def _process_completion(self, user_request: str, completion: dict) -> dict:
        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")
        completion["choices"][0]["text"] = completion["choices"][0]["text"].rstrip(
            "<|im_end|>",
        )
        # Add to chat history
        self.prompt.add_to_chat_history(
            "User: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + completion["choices"][0]["text"]
            + "<|im_end|>\n",
        )
        return completion

    def _process_completion_stream(self, user_request: str, completion: dict) -> str:
        full_response = ""
        for response in completion:
            if response.get("choices") is None:
                raise Exception("ChatGPT API returned no choices")
            if len(response["choices"]) == 0:
                raise Exception("ChatGPT API returned no choices")
            if response["choices"][0].get("finish_details") is not None:
                break
            if response["choices"][0].get("text") is None:
                raise Exception("ChatGPT API returned no text")
            if response["choices"][0]["text"] == "<|im_end|>":
                break
            yield response["choices"][0]["text"]
            full_response += response["choices"][0]["text"]

        # Add to chat history
        self.prompt.add_to_chat_history(
            "User: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + full_response
            + "<|im_end|>\n",
        )

    def ask(self, user_request: str, temperature: float = 0.5) -> dict:
        """
        Send a request to ChatGPT and return the response
        """
        completion = self._get_completion(
            self.prompt.construct_prompt(user_request),
            temperature,
        )
        return self._process_completion(user_request, completion)

    def ask_stream(self, user_request: str, temperature: float = 0.5) -> str:
        """
        Send a request to ChatGPT and yield the response
        """
        prompt = self.prompt.construct_prompt(user_request)
        return self._process_completion_stream(
            user_request=user_request,
            completion=self._get_completion(prompt, temperature, stream=True),
        )

    def rollback(self, num: int) -> None:
        """
        Rollback chat history num times
        """
        for _ in range(num):
            self.prompt.chat_history.pop()

    def reset(self) -> None:
        """
        Reset chat history
        """
        self.prompt.chat_history = []

    def load_conversation(self, conversation_id) -> None:
        """
        Load a conversation from the conversation history
        """
        self.prompt.chat_history = self.conversations.get_conversation(conversation_id)

    def save_conversation(self, conversation_id) -> None:
        """
        Save a conversation to the conversation history
        """
        self.conversations.add_conversation(conversation_id, self.prompt.chat_history)


class AsyncChatbot(Chatbot):
    """
    Official ChatGPT API (async)
    """

    async def _get_completion(
        self,
        prompt: str,
        temperature: float = 0.5,
        stream: bool = False,
    ):
        """
        Get the completion function
        """
        return openai.Completion.acreate(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=stream,
        )

    async def ask(self, user_request: str, temperature: float = 0.5) -> dict:
        """
        Same as Chatbot.ask but async
        }
        """
        completion = await self._get_completion(
            self.prompt.construct_prompt(user_request),
            temperature,
        )
        return self._process_completion(user_request, completion)

    async def ask_stream(self, user_request: str, temperature: float = 0.5) -> str:
        """
        Same as Chatbot.ask_stream but async
        """
        prompt = self.prompt.construct_prompt(user_request)
        return self._process_completion_stream(
            user_request=user_request,
            completion=await self._get_completion(prompt, temperature, stream=True),
        )


class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self, buffer: int = None) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = (
            os.environ.get("CUSTOM_BASE_PROMPT")
            or "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally. Current date: "
            + str(date.today())
            + "\n\n"
        )
        # Track chat history
        self.chat_history: list = []
        self.buffer = buffer

    def add_to_chat_history(self, chat: str) -> None:
        """
        Add chat to chat history for next prompt
        """
        self.chat_history.append(chat)

    def history(self) -> str:
        """
        Return chat history
        """
        return "\n".join(self.chat_history)

    def construct_prompt(self, new_prompt: str) -> str:
        """
        Construct prompt based on chat history and request
        """
        prompt = (
            self.base_prompt + self.history() + "User: " + new_prompt + "\nChatGPT:"
        )
        # Check if prompt over 4000*4 characters
        if self.buffer is not None:
            max_tokens = 4000 - self.buffer
        else:
            max_tokens = 3200
        if len(ENCODER.encode(prompt)) > max_tokens:
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt)
        return prompt


class Conversation:
    """
    For handling multiple conversations
    """

    def __init__(self) -> None:
        self.conversations = {}

    def add_conversation(self, key: str, history: list) -> None:
        """
        Adds a history list to the conversations dict with the id as the key
        """
        self.conversations[key] = history

    def get_conversation(self, key: str) -> list:
        """
        Retrieves the history list from the conversations dict with the id as the key
        """
        return self.conversations[key]

    def remove_conversation(self, key: str) -> None:
        """
        Removes the history list from the conversations dict with the id as the key
        """
        del self.conversations[key]

    def __str__(self) -> str:
        """
        Creates a JSON string of the conversations
        """
        return json.dumps(self.conversations)

    def save(self, file: str) -> None:
        """
        Saves the conversations to a JSON file
        """
        with open(file, "w", encoding="utf-8") as f:
            f.write(str(self))

    def load(self, file: str) -> None:
        """
        Loads the conversations from a JSON file
        """
        with open(file, encoding="utf-8") as f:
            self.conversations = json.loads(f.read())


def main():
    print(
        """
    ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
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
            !rollback - Rollback chat history
            !reset - Reset chat history
            !prompt - Show current prompt
            !save_c <conversation_name> - Save history to a conversation
            !load_c <conversation_name> - Load history from a conversation
            !save_f <file_name> - Save all conversations to a file
            !load_f <file_name> - Load all conversations from a file
            !exit - Quit chat
            """,
            )
        elif cmd == "!exit":
            exit()
        elif cmd == "!rollback":
            chatbot.rollback(1)
        elif cmd == "!reset":
            chatbot.reset()
        elif cmd == "!prompt":
            print(chatbot.prompt.construct_prompt(""))
        elif cmd.startswith("!save_c"):
            chatbot.save_conversation(cmd.split(" ")[1])
        elif cmd.startswith("!load_c"):
            chatbot.load_conversation(cmd.split(" ")[1])
        elif cmd.startswith("!save_f"):
            chatbot.conversations.save(cmd.split(" ")[1])
        elif cmd.startswith("!load_f"):
            chatbot.conversations.load(cmd.split(" ")[1])
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
        "--stream",
        action="store_true",
        help="Stream response",
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
        if not args.stream:
            response = chatbot.ask(prompt, temperature=args.temperature)
            print("ChatGPT: " + response["choices"][0]["text"])
        else:
            print("ChatGPT: ")
            sys.stdout.flush()
            for response in chatbot.ask_stream(prompt, temperature=args.temperature):
                print(response, end="")
                sys.stdout.flush()
            print()


if __name__ == "__main__":
    main()

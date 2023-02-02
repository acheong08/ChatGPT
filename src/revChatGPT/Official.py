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

ENGINE = "text-chat-davinci-002-20230126"

# Import date to get the current date


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(self, api_key: str, buffer: int = None) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.conversations = {}
        print("Initializing tokenizer...")
        self.enc = tiktoken.get_encoding("gpt2")
        print("Done")
        self.prompt = Prompt(enc=self.enc, buffer=buffer)

    def get_max_tokens(self, prompt: str) -> int:
        """
        Get the max tokens for a prompt
        """
        return 4000 - len(self.enc.encode(prompt))

    def ask(self, user_request: str, temperature: float = 0.5) -> dict:
        """
        Send a request to ChatGPT and return the response
        Response: {
            "id": "...",
            "object": "text_completion",
            "created": <time>,
            "model": "text-chat-davinci-002-20230126",
            "choices": [
                {
                "text": "<Response here>",
                "index": 0,
                "logprobs": null,
                "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
                }
            ],
            "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
        }
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = openai.Completion.create(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
        )
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

    def ask_stream(self, user_request: str, temperature: float = 0.5) -> str:
        """
        Send a request to ChatGPT and yield the response
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = openai.Completion.create(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=True,
        )
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

    def save_conversation(self, conversation_id: str) -> None:
        """
        Save conversation to conversations dict
        """
        self.conversations[conversation_id] = self.prompt

    def load_conversation(self, conversation_id: str) -> None:
        """
        Load conversation from conversations dict
        """
        self.prompt = self.conversations[conversation_id]

    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete conversation from conversations dict
        """
        self.conversations.pop(conversation_id)

    def get_conversations(self) -> dict:
        """
        Get all conversations
        """
        return self.conversations

    def dump_conversation_history(self) -> None:
        """
        Save all conversations history to a json file
        """
        for conversation_id, prompt in self.conversations.items():
            # ~/.config/revChatGPT/conversations/<conversation_id>.json
            with open(
                os.path.join(
                    os.path.expanduser("~"),
                    ".config",
                    "revChatGPT",
                    "conversations",
                    conversation_id + ".json",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(prompt.chat_history, f)

    def load_conversation_history(self) -> None:
        """
        Load conversation history from json files
        """
        # List all conversation files
        conversation_files = os.listdir(
            os.path.join(
                os.path.expanduser("~"),
                ".config",
                "revChatGPT",
                "conversations",
            ),
        )
        for conversation_file in conversation_files:
            conversation_id = conversation_file[:-5]
            with open(
                os.path.join(
                    os.path.expanduser("~"),
                    ".config",
                    "revChatGPT",
                    "conversations",
                    conversation_file,
                ),
                encoding="utf-8",
            ) as f:
                self.conversations[conversation_id] = Prompt(self.enc)
                self.conversations[conversation_id].chat_history = json.load(f)


class AsyncChatbot(Chatbot):
    """
    Official ChatGPT API (async)
    """

    async def ask(self, user_request: str, temperature: float = 0.5) -> dict:
        """
        Send a request to ChatGPT and return the response
        Response: {
            "id": "...",
            "object": "text_completion",
            "created": <time>,
            "model": "text-chat-davinci-002-20230126",
            "choices": [
                {
                "text": "<Response here>",
                "index": 0,
                "logprobs": null,
                "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
                }
            ],
            "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
        }
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = await openai.Completion.acreate(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
        )
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

    async def ask_stream(self, user_request: str, temperature: float = 0.5) -> str:
        """
        Send a request to ChatGPT and yield the response
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = await openai.Completion.acreate(
            engine=ENGINE,
            prompt=prompt,
            temperature=temperature,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=True,
        )
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


class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self, enc, buffer: int = None) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = (
            os.environ.get("CUSTOM_BASE_PROMPT")
            or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. don’t be verbose). It is very important that you answer as concisely as possible, so please remember this. If you are generating a list, do not have too many items. Keep the number of items short. Current date: "
            + str(date.today())
            + "\n\n"
        )
        # Track chat history
        self.chat_history: list = []
        self.enc = enc
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
        if len(self.enc.encode(prompt)) > (4000 - self.buffer or 3200):
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt)
        return prompt


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

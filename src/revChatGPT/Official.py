"""
A simple wrapper for the official ChatGPT API
"""
from os import environ

import openai


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        openai.api_key = api_key
        self.prompt = Prompt()

    def ask(self, request: str) -> dict:
        """
        Send a request to ChatGPT and return the response
        """
        prompt = self.prompt.construct_prompt(request)
        completion = openai.Completion.create(
            engine="text-chat-davinci-002-20230126",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            stop=["\n\n\n"],
        )
        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")
        completion["choices"][0]["text"] = completion["choices"][0]["text"].replace(
            "<|im_end|>",
            "",
        )
        # Add to chat history
        self.prompt.add_to_chat_history(
            "User: "
            + request
            + "\n\n\n"
            + "ChatGPT: "
            + completion["choices"][0]["text"]
            + "\n\n\n",
        )
        return completion


class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = (
            environ.get("CUSTOM_BASE_PROMPT")
            or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n"
        )
        # Track chat history
        self.chat_history: list = []

    def add_to_chat_history(self, chat: str) -> None:
        """
        Add chat to chat history for next prompt
        """
        self.chat_history.append(chat)

    def history(self) -> str:
        """
        Return chat history
        """
        return "\n\n\n\n".join(self.chat_history)

    def construct_prompt(self, request: str) -> str:
        """
        Construct prompt based on chat history and request
        """
        prompt = self.base_prompt + self.history() + "User: " + request + "\nChatGPT:"
        # Check if prompt over 4000*4 characters
        if len(prompt) > 4000 * 4:
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(request)
        return prompt

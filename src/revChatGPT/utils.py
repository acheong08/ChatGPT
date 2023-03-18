import re
from typing import Set

import requests
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()


def create_keybindings(key: str = "c-@") -> KeyBindings:
    """
    Create keybindings for prompt_toolkit. Default key is ctrl+space.
    For possible keybindings, see: https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html#list-of-special-keys
    """

    @bindings.add(key)
    def _(event: dict) -> None:
        event.app.exit(result=event.app.current_buffer.text)

    return bindings


def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def get_input(
    session: PromptSession = None,
    completer: WordCompleter = None,
    key_bindings: KeyBindings = None,
) -> str:
    """
    Multiline input function.
    """
    return (
        session.prompt(
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=key_bindings,
        )
        if session
        else prompt(multiline=True)
    )


async def get_input_async(
    session: PromptSession = None,
    completer: WordCompleter = None,
) -> str:
    """
    Multiline input function.
    """
    return (
        await session.prompt_async(
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
        )
        if session
        else prompt(multiline=True)
    )


def get_filtered_keys_from_object(obj: object, *keys: str) -> set[str]:
    """
    Get filtered list of object variable names.
    :param keys: List of keys to include. If the first key is "not", the remaining keys will be removed from the class keys.
    :return: List of class keys.
    """
    class_keys = obj.__dict__.keys()
    if not keys:
        return class_keys

    # Remove the passed keys from the class keys.
    if keys[0] == "not":
        return {key for key in class_keys if key not in keys[1:]}
    # Check if all passed keys are valid
    if invalid_keys := set(keys) - class_keys:
        raise ValueError(
            f"Invalid keys: {invalid_keys}",
        )
    # Only return specified keys that are in class_keys
    return {key for key in keys if key in class_keys}


class DataCollector:
    """
    Opt in data collection
    """

    def __init__(self, user: str) -> None:
        self.user = user

    def collect(self, prompt: str, message: dict) -> None:
        """
        Add message to conversation.
        """
        request = {
            "user": self.user,
            "id": message["conversation_id"],
            "message": {
                "prompt": prompt,
                "response": message["message"],
            },
        }
        # Send request to server
        requests.post(
            url="https://chatgpt-analytics.herokuapp.com/analytics/message",
            json=request,
            timeout=6,
        )

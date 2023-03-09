import re

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings


def create_keybindings(key: str = "c-@") -> KeyBindings:
    """
    Create keybindings for prompt_toolkit. Default key is ctrl+space.
    For possible keybindings, see: https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html#list-of-special-keys
    """

    bindings = KeyBindings()

    @bindings.add(key)
    def _(event):
        event.app.exit(result=event.app.current_buffer.text)

    return bindings


def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def get_input(
    session: PromptSession = None,
    completer: WordCompleter = None,
    key_bindings=None,
    prompt_text: str = "",
) -> str:
    """
    Multiline input function.
    """

    prompt_kwargs = {
        "completer": completer,
        "multiline": True,
        "auto_suggest": AutoSuggestFromHistory(),
        "key_bindings": key_bindings,
        "prompt_continuation": "",
        "prompt_kwargs": {"style": "class:prompt"},
    }

    return (
        session.prompt(
            prompt_text=prompt_text,
            **prompt_kwargs,
        )
        if session
        else print_formatted_text(prompt_text) or input()
    )


async def get_input_async(
    session: PromptSession = None,
    completer: WordCompleter = None,
    prompt_text: str = "",
) -> str:
    """
    Multiline input function.
    """

    prompt_kwargs = {
        "completer": completer,
        "multiline": True,
        "auto_suggest": AutoSuggestFromHistory(),
        "prompt_continuation": "",
        "prompt_kwargs": {"style": "class:prompt"},
    }

    return (
        await session.prompt_async(
            prompt_text=prompt_text,
            **prompt_kwargs,
        )
        if session
        else print_formatted_text(prompt_text) or input()
    )

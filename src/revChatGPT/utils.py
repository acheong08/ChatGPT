import re

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
    def _(event):
        event.app.exit(result=event.app.current_buffer.text)

    return bindings

def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def get_input(session: PromptSession = None, completer: WordCompleter = None, key_bindings = None) -> str:
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
    session: PromptSession = None, completer: WordCompleter = None
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

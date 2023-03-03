from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
import re

def create_session():
    session = PromptSession(history=InMemoryHistory())
    return session

def create_completer(commands: list, pattern_str: str = "$"):
    completer = WordCompleter(words=commands, pattern=re.compile(pattern_str))
    return completer

def get_input(session: PromptSession = None, completer: WordCompleter = None):
    """
    Multiline input function.
    """
    if session:
        user_input = session.prompt(
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
        )
    else:
        user_input = prompt(multiline=True)
    return user_input

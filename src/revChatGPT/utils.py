from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory


def create_session():
    session = PromptSession(history=InMemoryHistory())
    return session


def get_input(session=None):
    """
    Multiline input function.
    """
    if session:
        user_input = session.prompt(
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
        )
    else:
        user_input = prompt(multiline=True)
    return user_input

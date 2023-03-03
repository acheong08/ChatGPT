from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory


def create_session():
    return PromptSession(history=InMemoryHistory())


def get_input(session=None):
    """
    Multiline input function.
    """
    return (
        session.prompt(
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
        )
        if session
        else prompt(multiline=True)
    )

from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


def create_session():
    session = PromptSession(history=InMemoryHistory())
    return session


def get_input(prompt_prefix, session=None):
    """
    Multiline input function.
    """
    prefix = prompt_prefix + "(Press Esc followed by Enter to finish)\n"
    if session:
        user_input = session.prompt(
            prefix, multiline=True, auto_suggest=AutoSuggestFromHistory()
        )
    else:
        user_input = prompt(prefix, multiline=True)

    return user_input

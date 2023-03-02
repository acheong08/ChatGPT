from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory


def create_session():
    session = PromptSession(history=InMemoryHistory())
    return session


def get_input(session=None):
    """
    A function that reads multiple lines of user input.
    """
    if session:
        user_input = session.prompt(
            "Enter your input: \n",
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
        )
    else:
        user_input = input("Enter your input: \n")

    return user_input.strip()

from platform import python_version_tuple

SUPPORT = [int(each) for each in python_version_tuple()][0] >= 3 and [int(each) for each in python_version_tuple()][1] >= 11

class ChatbotError(Exception):
    """
    Base class for all Chatbot errors
    """

    def __init__(self, *args: object) -> None:
        if SUPPORT:
            super().add_note(
                "Please check that the input is correct, or you can resolve this issue by filing an issue"
            )
            super().add_note("Project URL: https://github.com/acheong08/ChatGPT")
        super().__init__(*args)

class Error(ChatbotError):
    """
    Base class for exceptions in V1 module.
    Error codes:
    -1: User error
    0: Unknown error
    1: Server error
    2: Rate limit error
    3: Invalid request error
    4: Expired access token error
    5: Invalid access token error
    6: Prohibited concurrent query error
    """

    source: str
    message: str
    code: int

    def __init__(self, source: str, message: str, code: int = 0, *args) -> None:
        self.source = source
        self.message = message
        self.code = code
        super().__init__(*args)

    def __str__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"

    def __repr__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"

class AuthenticationError(ChatbotError):
    pass

class APIConnectionError(ChatbotError):
    pass

class ResponseError(APIConnectionError):
    pass

class OpenAIError(APIConnectionError):
    pass


class RequestError(APIConnectionError):
    pass
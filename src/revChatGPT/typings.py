from abc import ABCMeta
from abc import abstractmethod
from os import getenv
from platform import python_version_tuple

Any = object()

SUPPORT = [int(each) for each in python_version_tuple()][0] >= 3 and [
    int(each) for each in python_version_tuple()
][1] >= 11
del python_version_tuple


class ChatbotError(Exception, metaclass=ABCMeta):
    """
    Base class for all Chatbot errors in this Project
    """

    @abstractmethod
    def __init__(self, *args: object) -> None:
        if SUPPORT:
            super().add_note(
                "Please check that the input is correct, or you can resolve this issue by filing an issue",
            )
            super().add_note("Project URL: https://github.com/acheong08/ChatGPT")
        super().__init__(*args)


class MetaNotAllowInstance(type):
    """
    Metaclasses that do not allow classes to be instantiated
    """

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        error = ActionNotAllowedError("This class is not allowed to be instantiated")
        raise error


class ActionError(ChatbotError):
    def __init__(self, *args: object) -> None:
        if SUPPORT:
            super().add_note(
                "The current operation is not allowed, which may be intentional"
            )
        super().__init__(*args)


class ActionNotAllowedError(ActionError):
    """
    Subclass of ActionError

    An object that throws an error because the execution of an unallowed operation is blocked
    """

    pass


class ActionRefuseError(ActionError):
    pass


class CLIError(ChatbotError):
    """
    Subclass of ChatbotError

    The error caused by a CLI program error
    """

    pass


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

    def __init__(self, source: str, message: str, code: int = 0, *args) -> None:
        self.source: str = source
        self.message: str = message
        self.code: int = code
        super().__init__(*args)

    def __str__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"

    def __repr__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"


class AuthenticationError(ChatbotError):
    """
    Subclass of ChatbotError

    The object of the error thrown by a validation failure or exception
    """

    def __init__(self, *args: object) -> None:
        if SUPPORT:
            super().add_note(
                "Please check if your key is correct, maybe it may not be valid"
            )
        super().__init__(*args)


class APIConnectionError(ChatbotError):
    """
    Subclass of ChatbotError

    An exception object thrown when an API connection fails or fails to connect due to network or other miscellaneous reasons
    """

    def __init__(self, *args: object) -> None:
        if SUPPORT:
            super().add_note(
                "Please check if there is a problem with your network connection"
            )
        super().__init__(*args)


class ResponseError(APIConnectionError):
    """
    Subclass of APIConnectionError

    Error objects caused by API request errors due to network or other miscellaneous reasons
    """

    pass


class OpenAIError(APIConnectionError):
    """
    Subclass of APIConnectionError

    Error objects caused by OpenAI's own server errors
    """

    pass


class RequestError(APIConnectionError):
    """
    Subclass of APIConnectionError

    There is a problem with the API response due to network or other miscellaneous reasons, or there is no reply to the object that caused the error at all
    """

    pass


class ErrorType(metaclass=MetaNotAllowInstance):
    # define consts for the error codes
    USER_ERROR = -1
    UNKNOWN_ERROR = 0
    SERVER_ERROR = 1
    RATE_LIMIT_ERROR = 2
    INVALID_REQUEST_ERROR = 3
    EXPIRED_ACCESS_TOKEN_ERROR = 4
    INVALID_ACCESS_TOKEN_ERROR = 5
    PROHIBITED_CONCURRENT_QUERY_ERROR = 6
    AUTHENTICATION_ERROR = 7
    CLOUDFLARE_ERROR = 8


class colors:
    """
    Colors for printing
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self) -> None:
        if getenv("NO_COLOR"):
            self.HEADER = ""
            self.OKBLUE = ""
            self.OKCYAN = ""
            self.OKGREEN = ""
            self.WARNING = ""
            self.FAIL = ""
            self.ENDC = ""
            self.BOLD = ""
            self.UNDERLINE = ""

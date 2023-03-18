from platform import python_version_tuple

class ChatbotError(Exception):
    """
    Base class for all Chatbot errors
    """
    def __init__(self, *args: object) -> None:
        _ = [int(each) for each in python_version_tuple()]
        if _[0] >= 3 and _[1] >= 11:
            super().add_note("Please check that the input is correct, or you can resolve this issue by filing an issue")
            super().add_note("Project URL: https://github.com/acheong08/ChatGPT")
        super().__init__(*args)

class APIConnectionError(ChatbotError):
    pass

class AuthenticationError(ChatbotError):
    pass

class OpenAIError(APIConnectionError):
    pass

class RequestError(APIConnectionError):
    pass
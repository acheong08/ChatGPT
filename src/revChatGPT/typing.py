class ChatbotError(Exception):
    """
    Base class for all Chatbot errors
    """
    pass

class APIConnectionError(ChatbotError):
    pass

class OpenAIError(APIConnectionError):
    pass

class RequestError(ChatbotError):
    pass

class AuthenticationError(ChatbotError):
    pass
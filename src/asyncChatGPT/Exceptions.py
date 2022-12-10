class ChatGPTException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class AuthError(ChatGPTException):
    pass


class ExpiredAccessToken(AuthError):
    pass


class InvalidAccessToken(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class APIError(ChatGPTException):
    pass


class NetworkError(ChatGPTException):
    pass


class HTTPError(NetworkError):
    pass


class HTTPStatusError(HTTPError):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

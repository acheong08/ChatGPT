from os import environ

from revChatGPT.revChatGPT import Chatbot

EMAIL = environ["OPENAI_EMAIL"]
PASSWORD = environ["OPENAI_PASSWORD"]

bot = Chatbot(EMAIL, PASSWORD, debug=True)

try:
    bot.refresh_session()
except Exception as e:
    print("Error:", e)
    assert False

try:
    response = bot.get_chat_response("Hello")
except Exception as e:
    print("Error:", e)
    assert False

try:
    if response['message'] is None:
        print("Error: response['message'] is None")
        assert False
except Exception as e:
    print("Error:", e)
    assert False

assert True

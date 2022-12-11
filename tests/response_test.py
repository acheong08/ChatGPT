from os import environ

from revChatGPT.revChatGPT import Chatbot

import base64

EMAIL = environ["OPENAI_EMAIL"]
PASSWORD = base64.b64decode(environ["OPENAI_PASSWORD"]).decode("utf-8")

config = {
    "email": EMAIL,
    "password": PASSWORD, }


bot = Chatbot(config=config, debug=True)

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

print("Success!")
assert True

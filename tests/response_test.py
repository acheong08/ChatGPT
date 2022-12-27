from os import environ

from revChatGPT.ChatGPT import Chatbot

import base64

EMAIL = environ["OPENAI_EMAIL"]
PASSWORD = base64.b64decode(environ["OPENAI_PASSWORD"]).decode("utf-8")

config = {
    "email": EMAIL,
    "password": PASSWORD, }


def test_response():
    try:
        bot = Chatbot(config=config, debug=True)

        bot.refresh_session()

        response = bot.get_chat_response("Hello")

        if response['message'] is None:
            print("Error: response['message'] is None")
            assert False
        else:
            print(f"response['message']: {response['message']}")

        print("Success!")
    except Exception as exc:
        print(f"Error: {exc}")
        assert False
    assert True

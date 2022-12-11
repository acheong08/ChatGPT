from os import environ
import json

from OpenAIAuth.OpenAIAuth import OpenAIAuth

EMAIL = environ["OPENAI_EMAIL"]
PASSWORD = environ["OPENAI_PASSWORD"]

auth = OpenAIAuth(EMAIL, PASSWORD, debug=True, use_captcha=False)

try:
    auth.begin()
except Exception as e:
    print("Error:", e)
    assert False

if auth.access_token is None:
    print("Error: access_token is None")
    assert False

try:
    possible_tokens = auth.session.cookies.get(
        "__Secure-next-auth.session-token",
    )
    if possible_tokens is None:
        print("Error: __Secure-next-auth.session-token is None")
        assert False
    else:
        if len(possible_tokens) > 1:
            session_token = possible_tokens[0]
        else:
            session_token = possible_tokens
except Exception as e:
    print("Error:", e)
    assert False

# Save the access token and session token to a file
config = {
    "Authorization": auth.access_token,
    "session_token": session_token
}

with open("config.json", "w", encoding='utf-8') as f:
    json.dump(config, f, indent=4)


print("Success!")
assert True

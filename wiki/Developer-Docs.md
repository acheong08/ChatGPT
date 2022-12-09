# Development

## Standard use

### Initial setup

`pip3 install revChatGPT --upgrade`

```python
from revChatGPT.revChatGPT import Chatbot

# For the config please go here:
# https://github.com/acheong08/ChatGPT/wiki/Setup
config = {
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>"#,
    #"session_token": "<SESSION_TOKEN>", # Deprecated. Use only if you encounter captcha with email/password
    #"proxy": "<HTTP/HTTPS_PROXY>"
}

chatbot = Chatbot(config, conversation_id=None)
```

### Chatbot functions

```python
    def __init__(self, config, conversation_id=None, debug=False, refresh=True):
        """
        :param config: Config dict
        :param conversation_id: Conversation ID. If None, a new conversation will be created
        :param debug: Debug mode, Default is False
        :param refresh: Refresh the session token, Default is True
        """
    def reset_chat(self): -> None
    def refresh_headers(self): -> None
    def generate_uuid(self): # Internal use
    def get_chat_stream(self, data): # Internal
    def get_chat_text(self, data): # Internal
    def get_chat_response(self, prompt, output="text"):
        """
        :param prompt: The message sent to the chatbot
        :param output: Output type. Can be "text" or "stream"
        :return: Response from the chatbot
        """
    def rollback_conversation(self):
        """
        Rollback the conversation to the previous state
        :return: None
        """
    def refresh_session(self):
        """
        Refresh the session token
        :return: None
        """
    def login(self, email, password):
        """
        :param email: Email
        :param password: Password
        """
```

## Getting responses

Output options: `text`, `stream`

```python
... # After the initial setup
# The text output

response = chatbot.get_chat_response("Hello world", output="text")
print(response) 

# returns {'message':message, 'conversation_id':self.conversation_id, 'parent_id':self.parent_id}
```

```python
# The stream output
response = chatbot.get_chat_response("Hello world", output="stream")
for res in response:
    print(res['message'])

# returns {'message':message, 'conversation_id':self.conversation_id, 'parent_id':self.parent_id}
```

## Async use

### Initial setup

`pip3 install revChatGPT --upgrade`

```python
from asyncChatGPT.asyncChatGPT import Chatbot

# For the config please go here:
# https://github.com/acheong08/ChatGPT/wiki/Setup
config = {
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>"#,
    #"session_token": "<SESSION_TOKEN>", # Deprecated. Use only if you encounter captcha with email/password
    #"proxy": "<HTTP/HTTPS_PROXY>"
}

chatbot = Chatbot(config, conversation_id=None)
```

<details>
<summary>

### Get text response

</summary>

example use:

```python
... # After the initial setup
import asyncio
message = asyncio.run(chatbot.get_chat_response("Hello world"))['message']
print(message)
```

</details>

<details>
<summary>

### Get streaming response

</summary>

example use:

```python
... # After the initial setup
import asyncio
async def printMessage():
    async for i in await chatbot.get_chat_response("hello", output="stream"):
        print(i['message'])
asyncio.run(printMessage())
```

</details>

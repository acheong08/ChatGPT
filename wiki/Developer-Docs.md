# Development
Full API docs: [here](https://github.com/acheong08/ChatGPT/wiki/revChatGPT)

## Standard use

### Initial setup

`pip3 install revChatGPT --upgrade`

```python
from revChatGPT.revChatGPT import Chatbot

# For the config please go here:
# https://github.com/acheong08/ChatGPT/wiki/Setup
config = {
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>",
    #"session_token": "<SESSION_TOKEN>", # Deprecated. Use only if you encounter captcha with email/password
    #"proxy": "<HTTP/HTTPS_PROXY>"
}

chatbot = Chatbot(config, conversation_id=None)
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
from revChatGPT.revChatGPT import AsyncChatbot as Chatbot

# For the config please go here:
# https://github.com/acheong08/ChatGPT/wiki/Setup
config = {
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>",
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

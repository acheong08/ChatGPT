# Development

## Standard use
### Initial setup
`pip3 install revChatGPT --upgrade`
```python
import from revChatGPT.revChatGPT import Chatbot

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
    def __init__(self, config, conversation_id=None):
    def reset_chat(self): -> None
    def refresh_headers(self): -> None
    def generate_uuid(self): # Internal use
    def get_chat_stream(self, data): # Internal
    def get_chat_text(self, data): # Internal
    def get_chat_response(self, prompt, output="text")
    def rollback_conversation(self):
    def refresh_session(self):
    def login(self, email, password):
```
##  Getting responses
Output options: `text`, `stream`
```python
... # After the initial setup
response = chatbot.get_chat_response("Hello world")
print(response) #returns {'message':message, 'conversation_id':self.conversation_id, 'parent_id':self.parent_id}
```

## Async use
### Initial setup
`pip3 install revChatGPT --upgrade`
```python
import from revChatGPT.asyncChatGPT import Chatbot

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

###  Get streaming response
</summary>

example use:
```python
... # After the initial setup
import asyncio
async def printMessage():
    async for i in await chatbot.get_chat_response("hello", output="stream"):
        print(i['message'])
asyncio.run(get_res())
```
</details>

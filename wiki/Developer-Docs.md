# TODO

```py
from revChatGPT.revChatGPT import Chatbot

# Do some config
...


chatbot = Chatbot({
   # This could be blank but the dict should be here
})

chatbot.get_chat_response(prompt, output="text") #output=stream uses async generator
```

Example: https://github.com/acheong08/ChatGPT/blob/main/src/revChatGPT/__main__.py
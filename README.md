# ChatGPT
Reverse Engineered ChatGPT by OpenAI. Extensible for chatbots etc.

# Announcement:
If you were using this prior to version 0.0.24, please update immediately. `pip3 install revChatGPT --upgrade`. Fixes has been done to avoid bot blocking.

# Disclaimer
This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

### This is a library and not intended for direct CLI use
The CLI functionality is for demo and testing only.

## CLI use
[@rawandahmad698](https://github.com/rawandahmad698) has a much better CLI tool at

**[PyChatGPT](https://github.com/rawandahmad698/PyChatGPT)**

## Urgent help needed
- Writing tests
- More verbose error handling
- Decrecate bs4 in favor of pure requests
### Wiki is now open to all contributors

# Features
![image](https://user-images.githubusercontent.com/36258159/205534498-acc59484-c4b4-487d-89a7-d7b884af709b.png)
- No moderation
- Programmable

# Setup
## Install
`pip3 install revChatGPT --upgrade`

## Email and password authentication
```json
{
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>"
}
```
Save this in `config.json` in current working directory

<details>
<summary>
## Token Authentication
</summary>
Go to https://chat.openai.com/chat and log in or sign up

1. Open console with `F12`
2. Open `Application` tab > Cookies
![image](https://user-images.githubusercontent.com/36258159/205494773-32ef651a-994d-435a-9f76-a26699935dac.png)
3. Copy the value for `__Secure-next-auth.session-token` and paste it into `config.json.example` under `session_token`. You do not need to fill out `Authorization`
![image](https://user-images.githubusercontent.com/36258159/205495076-664a8113-eda5-4d1e-84d3-6fad3614cfd8.png)
4. Save the modified file to `config.json` (In the current working directory)
</details>

# Running
```
 $ python3 -m revChatGPT            

    ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
    Repo: github.com/acheong08/ChatGPT
    Arguments: Use --stream to enable data streaming. (Doesn't work on MacOS)
    
Type '!help' to show commands
Press enter twice to submit your question.

You: !help


                !help - Show this message
                !reset - Forget the current conversation
                !refresh - Refresh the session authentication
                !exit - Exit the program
```

Refresh every so often in case the token expires.

# Development:
`pip3 install revChatGPT --upgrade`
```python
from revChatGPT.revChatGPT import Chatbot
import json

# Get your config in JSON
config = {
    "email": "<YOUR_EMAIL>",
    "password": "<YOUR_PASSWORD>"
}

chatbot = Chatbot(config, conversation_id=None)
chatbot.reset_chat() # Forgets conversation
chatbot.refresh_session() # Uses the session_token to get a new bearer token
resp = chatbot.get_chat_response(prompt, output="text") # Sends a request to the API and returns the response by OpenAI
resp['message'] # The message sent by the response
resp['conversation_id'] # The current conversation id
resp['parent_id'] # The ID of the response

 # This returns a stream of text (live update)
resp = chatbot.get_chat_response(prompt, output="stream") 
for line in resp: # You have to loop through the response stream
        print(line['message']) # Same format as text return type
        ...
```
This can be imported to projects for bots and much more. You can have multiple independent conversations by keeping track of the conversation_id.

# Awesome ChatGPT
[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Star History

[![Star History Chart](https://api.star-history.com/svg?repos=acheong08/ChatGPT&type=Date)](https://star-history.com/#acheong08/ChatGPT&Date)

# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

> ## Support my work
> Make a pull request and fix my bad code.

Discord community: https://discord.gg/WMNtbDUjUv

# V1 Standard ChatGPT
> ## Update 2023/02/14 9:00 PM GMT+8: It is working. Use this.

## Installation
`pip3 install revChatGPT`

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

### Authentication method: (Choose 1)
#### Email/Password
Not supported for Google/Microsoft accounts
```json
{
  "email": "email",
  "password": "your password"
}
```
#### Session token
Comes from cookies on chat.openai.com as "__Secure-next-auth.session-token"

```json
{
  "session_token": "..."
}
```
#### Access token
https://chat.openai.com/api/auth/session
```json
{
  "access_token": "<access_token>"
}
```

#### Optional configuration:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
  "paid": false
}
```

3. Save this as `$HOME/.config/revChatGPT/config.json`
4. If you are using Windows, you will need to create an environment variable named ```HOME``` and set it to your home profile for the script to be able to locate the config.json file.

## Usage

### Command line

`python3 -m revChatGPT.V1`

```
!help - Show this message
!reset - Forget the current conversation
!config - Show the current configuration
!rollback x - Rollback the conversation (x being the number of messages to rollback)
!exit - Exit this program
```

### Developer API

#### Basic example (streamed):
```python
from revChatGPT.V1 import Chatbot

chatbot = Chatbot(config={
  "email": "<your email>",
  "password": "<your password>"
})

print("Chatbot: ")
prev_text = ""
for data in chatbot.ask(
    "Hello world",
):
    message = data["message"][len(prev_text) :]
    print(message, end="", flush=True)
    prev_text = data["message"]
print()
```

#### Basic example (single result):

```python
from revChatGPT.V1 import Chatbot

chatbot = Chatbot(config={
  "email": "<your email>",
  "password": "<your password>"
})

prompt = "how many beaches does portugal have?"
response = ""

for data in chatbot.ask(
  prompt
):
    response = data["message"]

print(response)
```
#### All API methods
Refer to the [wiki](https://github.com/acheong08/ChatGPT/wiki/V1) for advanced developer usage.


# V2 Fast ChatGPT API

> ## Under maintenance

Using cloudflare bypass server (no browser on server either). Check out the server source code: https://github.com/acheong08/ChatGPT-Proxy-V2

> ### Notices
> It seems I wasn't clear enough in my explanations and lead to some misunderstandings:
> - Your email and password are not sent to me. Authentication is done locally with https://github.com/acheong08/OpenAIAuth
>  - *Unless you use `--insecure-auth`*. This is meant for users who are blocked from accessing OpenAI websites
> - The server is open source: https://github.com/acheong08/ChatGPT-Proxy-V2 but with a `config.json` missing to avoid OpenAI detection.
> - Rate limits: 180 requests per minute (IP based)
> - I am running the server right now

> ## IMPORTANT
> You must either define `--paid` in command line or `paid=True` in code if you have a plus subscription.

## Usage

`pip3 install --upgrade revChatGPT`

```
 $ python3 -m revChatGPT.V2 -h

        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT

usage: V2.py [-h] [-e EMAIL] [-p PASSWORD] [--paid] [--proxy PROXY] [--insecure-auth]
             [--session_token SESSION_TOKEN]

options:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Your OpenAI email address
  -p PASSWORD, --password PASSWORD
                        Your OpenAI password
  --paid                Use the paid API
  --proxy PROXY         Use a proxy
  --insecure-auth       (Deprecated)
  --session_token SESSION_TOKEN Alternative to email and password authentication. Use this if you have Google/Microsoft account.
```

## Developers
Wiki: https://github.com/acheong08/ChatGPT/wiki/V2

Example code:
```python
from revChatGPT.V2 import Chatbot

async def main():
    chatbot = Chatbot(email="...", password="...")
    async for line in chatbot.ask("Hello"):
        print(line["choices"][0]["text"].replace("<|im_end|>", ""), end="", flush = True)
    print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```


# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

# Credits

- [virtualharby](https://twitter.com/virtualharby) - Memes for emotional support
- [All contributors](https://github.com/acheong08/ChatGPT/graphs/contributors) - Pull requests

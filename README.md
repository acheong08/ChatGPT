# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

Connect with me on [Linkedin](https://www.linkedin.com/in/acheong08/) to support this project. (Not open for commercial opportunities yet. Too busy)
<br><br>
You can also follow me on [Twitter](https://twitter.com/GodlyIgnorance) to stay up to date.

> ## [BingGPT](https://github.com/acheong08/BingGPT) is out! It's just like ChatGPT but with live internet access. Reverse engineered from the pre-release by Microsoft.
> You need to be waitlisted by Microsoft/Bing

# V2 Browserless ChatGPT

`pip3 install --upgrade revChatGPT`

```bash
 $ python3 -m revChatGPT.V2 -h

        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT

usage: V2.py [-h] -e EMAIL -p PASSWORD

options:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Your OpenAI email address
  -p PASSWORD, --password PASSWORD
                        Your OpenAI password
```

## Developers
Wiki: https://github.com/acheong08/ChatGPT/wiki/V2

Example code:
```python
from revChatGPT.V2 import Chatbot

async def main():
    chatbot = Chatbot(email="...", password="...")
    async for line in chatbot.ask("Hello"):
        print(line["choices"][0]["text"].replace("<|im_end|>", ""), end="")
        sys.stdout.flush()
    print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

<details>

<summary>

# Outdated V1 versions
</summary>

# V1.1 Proxy API

> ## Update 2023/02/11 - I am getting DDOSed. I might not be able to keep hosting it. Use V1 or host a bypass server yourself

The proxy is identical to V1 but uses a proxy to bypass the browser automation. This is the recommended version. You can read up on the documentation below

## Differences:
- Automatic session refresh on client side
- Browserless

```python
from revChatGPT.Proxied import Chatbot
```

## Notes
Proxy server is open source at https://github.com/acheong08/ChatGPT-Proxy

## Usage
- Save your email and password to `$HOME/.config/revChatGPT/config.json`
```json
{"email": "<your username>", "password": "<your password>"}
```

`python3 -m revChatGPT.Proxied`


<details>
<summary>

# V1 Browser automation

Browser is required on startup to fetch cookies. Breaks terms of service.

</summary>

## Installation
`pip3 install revChatGPT`

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

Required configuration:

```json
{
  "email": "<your email>",
  "password": "your password",
}
```

Optional configuration:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
  "paid": false
}
```

3. Save this as `$HOME/.config/revChatGPT/config.json`

## Usage

### Command line

`python3 -m revChatGPT.Unofficial`

```
!help - Show this message
!reset - Forget the current conversation
!refresh - Refresh the session authentication
!config - Show the current configuration
!rollback x - Rollback the conversation (x being the number of messages to rollback)
!exit - Exit this program
```

### Developer

```python
from revChatGPT.Unofficial import Chatbot

chatbot = Chatbot({
  "email": "<your email>",
  "password": "your password"
}, conversation_id=None, parent_id=None) # You can start a custom conversation

response = chatbot.ask("Prompt", conversation_id=None, parent_id=None) # You can specify custom conversation and parent ids. Otherwise it uses the saved conversation (yes. conversations are automatically saved)

print(response)
# {
#   "message": message,
#   "conversation_id": self.conversation_id,
#   "parent_id": self.parent_id,
# }
```

Refer to [wiki](https://github.com/acheong08/ChatGPT/wiki/V1---Outdated-version) for advanced developer usage

<details>

<summary>

### API
`python3 -m revChatGPT.GPTserver`

</summary>

HTTP POST request:

```json
{
  "session_token": "eyJhbGciOiJkaXIiL...",
  "prompt": "Your prompt here"
}
```

Optional:

```json
{
  "session_token": "eyJhbGciOiJkaXIiL...",
  "prompt": "Your prompt here",
  "conversation_id": "UUID...",
  "parent_id": "UUID..."
}
```

- Rate limiting is enabled by default to prevent simultaneous requests

</details>

</details>

</details>

# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

# Credits

- [virtualharby](https://twitter.com/virtualharby) - Memes for emotional support
- [All contributors](https://github.com/acheong08/ChatGPT/graphs/contributors) - Pull requests

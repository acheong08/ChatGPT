# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

Connect with me on [Linkedin](https://www.linkedin.com/in/acheong08/) to support this project. (Not open for commercial opportunities yet. Too busy)
<br><br>
You can also follow me on [Twitter](https://twitter.com/GodlyIgnorance) to stay up to date.

> ## This repository is updated highly frequently. Expect breaking changes. Always read docs and readme before updating or opening an issue

<details>
<summary>

# Base model API

> ## Update 2023/02/08: This model has been revoked by OpenAI. We are working towards a new model.
> As a temporary workaround, set environment variable `export GPT_ENGINE="text-davinci-003"` (Costs credit)

</summary>

## Installation
`pip3 install revChatGPT`

## Setup

1. Create account on [OpenAI](https://platform.openai.com/)
2. Go to https://platform.openai.com/account/api-keys
3. Copy API key

## Usage

### Command line
`python3 -m revChatGPT.Official --api_key API_KEY --stream`

<details>
<summary>

### Developer
</summary>

Both Async and Sync are available. You can also stream responses via a generator. Read example code to learn more

#### Example code

You can find it [here](https://github.com/acheong08/ChatGPT/blob/main/src/revChatGPT/Official.py#L292-L408)

#### Further Documentation
You can find it [wiki](https://github.com/acheong08/ChatGPT/wiki/revChatGPT)

</details>
</details>

<details>
<summary>

# ChatGPT website version

Browser is required. Breaks terms of service. No longer supported by developer

</summary>

## Installation
`pip3 install revChatGPT[unofficial]`

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

Required configuration:

```json
{
  "email": "<your email>",
  "password": "your password"
}
```

Optional configuration:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
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

# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

# Credits

- [virtualharby](https://twitter.com/virtualharby) - Memes for emotional support
- [All contributors](https://github.com/acheong08/ChatGPT/graphs/contributors) - Pull requests

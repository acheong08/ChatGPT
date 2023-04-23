# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

English - [中文](./README_zh.md) - [Spanish](./README_sp.md) -  [日本語](./README_ja.md)

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Support_Platform](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

[![](https://github.com/acheong08/ChatGPT/blob/main/docs/view.gif?raw=true)](https://pypi.python.org/pypi/revChatGPT)

> ## Support my work
>
> Make a pull request and fix my bad code.
>
> [![support](https://ko-fi.com/img/githubbutton_sm.svg)](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

> #### Discord Server: https://discord.gg/9K2BvbXEHT

# Installation

```
python -m pip install --upgrade revChatGPT
```

### Suport Python Version

- Minimum - Python3.9
- Recommend - Python3.11+

<details>

  <summary>

# V1 Standard ChatGPT

Due to recent tightening of OpenAI's security, the default endpoint has been swapped over to one provided by @pengzhile. It is not open source and privacy is not guarenteed. Use it at your own risk. I am working on an open source implementation with the latest changes but that could take a while.

</summary>

## Rate limits
- Proxy server: 5 requests / 10 seconds
- OpenAI: 50 requests / hour for each account

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

### Authentication method: (Choose 1)

#### - Email/Password

> _Currently broken for free users. Do `export PUID="..."` if you have a plus account. The PUID is a cookie named `_puid`_
> Not supported for Google/Microsoft accounts.
```json
{
  "email": "email",
  "password": "your password"
}
```

#### - Access token

> Please this!
https://chat.openai.com/api/auth/session

```json
{
  "access_token": "<access_token>"
}
```

#### - Optional configuration:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
  "paid": false,
  "collect_analytics": true,
  "model": "gpt-4"
}
```

Analytics is disabled by default. Set `collect_analytics` to `true` to enable it.

3. Save this as `$HOME/.config/revChatGPT/config.json`
4. If you are using Windows, you will need to create an environment variable named `HOME` and set it to your home profile for the script to be able to locate the config.json file.

## Usage

### Command line

`python3 -m revChatGPT.V1`

```
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
Type '!help' to show a full list of commands
Logging in...
You:
(Press Esc followed by Enter to finish)
```

The command line interface supports multi-line inputs and allows navigation using arrow keys. Besides, you can also edit history inputs by arrow keys when the prompt is empty. It also completes your input if it finds matched previous prompts. To finish input, press `Esc` and then `Enter` as solely `Enter` itself is used for creating new line in multi-line mode.

Set the environment variable `NO_COLOR` to `true` to disable color output.

### Developer API

#### Basic example (streamed):

```python
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": "<your access_token>"
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
  "access_token": "<your access_token>"
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

Refer to the [wiki](https://github.com/acheong08/ChatGPT/wiki/) for advanced developer usage.

</details>

<summary>

# V3 Official Chat API

> Recently released by OpenAI
>
> - Paid

</summary>

Get API key from https://platform.openai.com/account/api-keys

## Command line

`python3 -m revChatGPT.V3 --api_key <api_key>`

```
  $ python3 -m revChatGPT.V3 --help

    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT

Type '!help' to show a full list of commands
Press Esc followed by Enter or Alt+Enter to send a message.

usage: V3.py [-h] --api_key API_KEY [--temperature TEMPERATURE] [--no_stream] [--base_prompt BASE_PROMPT]
             [--proxy PROXY] [--top_p TOP_P] [--reply_count REPLY_COUNT] [--enable_internet]
             [--config CONFIG] [--submit_key SUBMIT_KEY] [--model {gpt-3.5-turbo,gpt-4,gpt-4-32k}]
             [--truncate_limit TRUNCATE_LIMIT]

options:
  -h, --help            show this help message and exit
  --api_key API_KEY     OpenAI API key
  --temperature TEMPERATURE
                        Temperature for response
  --no_stream           Disable streaming
  --base_prompt BASE_PROMPT
                        Base prompt for chatbot
  --proxy PROXY         Proxy address
  --top_p TOP_P         Top p for response
  --reply_count REPLY_COUNT
                        Number of replies for each prompt
  --enable_internet     Allow ChatGPT to search the internet
  --config CONFIG       Path to V3 config json file
  --submit_key SUBMIT_KEY
                        Custom submit key for chatbot. For more information on keys, see README
  --model {gpt-3.5-turbo,gpt-4,gpt-4-32k}
  --truncate_limit TRUNCATE_LIMIT
```

## Developer API

### Basic example

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
chatbot.ask("Hello world")
```

### Streaming example

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
for data in chatbot.ask_stream("Hello world"):
    print(data, end="", flush=True)
```

</details>

# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me.

## Contributors

This project exists thanks to all the people who contribute.

<a href="https://github.com/acheong08/ChatGPT/graphs/contributors">
<img src="https://contrib.rocks/image?repo=acheong08/ChatGPT" />
</a>

## Additional credits

- Coding while listening to [this amazing song](https://www.youtube.com/watch?v=VaMR_xDhsGg) by [virtualharby](https://www.youtube.com/@virtualharby)

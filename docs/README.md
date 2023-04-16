# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

English - [中文](./README_zh.md)

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Support_Platform](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

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

# V1 disabled
- Cloudflare has tightened their security and thus the current tls spoofing libraries no longer work with cf_clearance. OpenAI also removed the ability of ChatGPT Plus users to bypass cloudflare. This will not work until further notice 

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

# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

> ## Support my work
> Make a pull request and fix my bad code.

# Installation
`pip3 install --upgrade revChatGPT`

<details>

<summary>

# V1 Standard ChatGPT
> Update 2023/03/10 11:00AM - Everything works
> > 3:35 PM - Rate limit at 5 requests / 10 seconds due to small server (I ran out of budget.)

> ### [Privacy policy](https://github.com/acheong08/ChatGPT/blob/main/PRIVACY.md)
> <br>
>
> #### [Discussion regarding data collection](https://github.com/acheong08/ChatGPT/discussions/1147)

> :warning: **Avoid untrusted servers**. It was discovered today that access tokens can also be used to call the paid API. If your token is logged, it could be easily abused and cost you money.

</summary>

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

### Authentication method: (Choose 1)
#### - Email/Password
Not supported for Google/Microsoft accounts
```json
{
  "email": "email",
  "password": "your password"
}
```
#### - Session token
Comes from cookies on chat.openai.com as "__Secure-next-auth.session-token"

```json
{
  "session_token": "..."
}
```
#### - Access token
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
4. If you are using Windows, you will need to create an environment variable named ```HOME``` and set it to your home profile for the script to be able to locate the config.json file.

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

</details>


<details>

<summary>

# V3 Official Chat API
> Recently released by OpenAI
> - Paid

</summary>

Get API key from https://platform.openai.com/account/api-keys

## Command line
`python3 -m revChatGPT.V3 --api_key <api_key>`

```
 $ python3 -m revChatGPT.V3 -h

    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT

Type '!help' to show a full list of commands
Press Esc followed by Enter or Alt+Enter to send a message.

usage: V3.py [-h] --api_key API_KEY [--temperature TEMPERATURE] [--no_stream] [--base_prompt BASE_PROMPT] [--proxy PROXY] [--top_p TOP_P]
             [--reply_count REPLY_COUNT] [--enable_internet] [--config CONFIG] [--submit_key SUBMIT_KEY]

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
                        Custom submit key for chatbot. For more information on keys, see https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html#list-of-special-keys
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
for data in chatbot.ask("Hello world"):
    print(data, end="", flush=True)
```

</details>

# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me.

# Credits

- [virtualharby](https://twitter.com/virtualharby) - Memes for emotional support
- [All contributors](https://github.com/acheong08/ChatGPT/graphs/contributors) - Pull requests

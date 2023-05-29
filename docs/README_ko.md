# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

English - [中文](./README_zh.md) - [Spanish](./README_sp.md) -  [日本語](./README_ja.md) - [한국어](./README_ko.md)

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Support_Platform](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

OpenAI가 개발한 ChatGPT API를 Reverse-Engineering한 프로젝트입니다. 본 프로젝트를 통해 챗봇 등의 확장 가능한 목적으로 사용할 수 있습니다.

[![](https://github.com/acheong08/ChatGPT/blob/main/docs/view.gif?raw=true)](https://pypi.python.org/pypi/revChatGPT)

# 설치

```
python -m pip install --upgrade revChatGPT
```

### 지원 가능한 파이썬 버전

- Minimum - Python3.9
- Recommend - Python3.11+

<details>

  <summary>

# V1 Standard ChatGPT

V1은 모두에게 편리한 사용을 위해 클라우드플레어 우회 프록시를 사용합니다. 이 프록시는 오픈 소스로 제공됩니다: https://github.com/acheong08/ChatGPT-Proxy-V4

자체 배포한 프록시를 설정하려면 환경 변수 CHATGPT_BASE_URL을 https://yourproxy.com/api/로 설정하십시오.

</summary>

## Rate limits
- Proxy server: 5 requests / 10 seconds
- OpenAI: 50 requests / hour for each account

## Configuration

1. Create account on [OpenAI's ChatGPT](https://chat.openai.com/)
2. Save your email and password

### Authentication method: (Choose 1)

#### - Email/Password

> Not supported for Google/Microsoft accounts.
```json
{
  "email": "email",
  "password": "your password"
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
  "model": "gpt-4", // gpt-4-browsing, text-davinci-002-render-sha, gpt-4, gpt-4-plugins
  "plugin_ids" : ["plugin-d1d6eb04-3375-40aa-940a-c2fc57ce0f51"], // Wolfram Alpha example
  "disable_history": true,
}
```

1. 위 내용을 $HOME/.config/revChatGPT/config.json로 저장하세요.
2. Windows를 사용하는 경우, 스크립트가 config.json 파일을 찾을 수 있도록 환경 변수인 HOME을 생성하고 홈 프로필로 설정하셔야 합니다.

Plugin IDs는 다음 [링크](./plugins.json)를 참조하세요.  만약 플러그인이 활성화되어 있다면, 모델을 gpt-4-plugins로 설정하세요. 웹 인터페이스에서 플러그인을 설치하지 않은 경우 플러그인이 작동할 수도 있고 작동하지 않을 수도 있습니다. 코드에서 chatbot.install_plugin(plugin_id=plugin_id)를 호출하여 플러그인 중 하나를 설치할 수 있습니다. chatbot.get_plugins()를 호출하여 사용 가능한 모든 플러그인 목록을 확인하실 수 있습니다.

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

Command line 인터페이스는 여러 줄의 입력을 지원하며, 화살표 키를 사용하여 탐색할 수 있습니다. 또한, 프롬프트가 비어있을 때 화살표 키를 사용하여 이전 입력을 편집할 수도 있습니다. 이전 프롬프트와 일치하는 내용을 찾으면 입력을 자동 완성하며, 입력을 완료하려면 Esc를 누른 다음에 Enter를 누르세요. Enter키만 누르면 여러 줄 모드에서 새 줄을 생성합니다.

컬러 출력을 비활성화하려면 환경 변수 NO_COLOR를 true로 설정하세요.

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

<details>

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

만약 추가하고 싶은 멋진 프로젝트가 있다면, 이슈를 생성해주세요.

# Disclaimers

이것은 공식적인 OpenAI Product가 아니며, 개인 프로젝트로 OpenAI와 어떠한 관련도 없습니다. 본 코드의 사용으로 인한 어떠한 책임도 지지 않습니다.

## Contributors

이 프로젝트는 기여해 주신 모든 분들에게 감사드립니다.

<a href="https://github.com/acheong08/ChatGPT/graphs/contributors">
<img src="https://contrib.rocks/image?repo=acheong08/ChatGPT" />
</a>

## Additional credits

- Coding while listening to [this amazing song](https://www.youtube.com/watch?v=VaMR_xDhsGg) by [virtualharby](https://www.youtube.com/@virtualharby)

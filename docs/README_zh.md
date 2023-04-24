# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

[English](./README.md) - 中文 - [Spanish](./README_sp.md) -  [日本語](./README_ja.md)

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![支持的平台](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

ChatGPT 的逆向工程可扩展 API，可用于聊天机器人等。

[![](https://github.com/acheong08/ChatGPT/blob/main/docs/view.gif?raw=true)](https://pypi.python.org/pypi/revChatGPT)

> ## 支持本项目
> 开 Pull Request 并修复我的代码

> #### Discord 服务器: https://discord.gg/9K2BvbXEHT

# 安装

```
python -m pip install --upgrade revChatGPT
```

### 支持的Python版本
- 最低版本 - Python3.9
- 推荐版本 - Python3.11+


<details>

<summary>

# V1 标准 ChatGPT

通过对 `chat.openai.com` API 进行逆向工程，再[绕过Cloudflare Server](https://github.com/acheong08/ChatGPT-Proxy-V4)，以免费使用 ChatGPT API。由于 OpenAI 严格的访问频率限制，此特定库仅供个人使用。尚未针对多帐户进行优化。

您也可以查看此[项目](https://github.com/acheong08/ChatGPT-to-API)用于搭建多账户循环调用系统，鉴于它与官方 API 兼容。使用 [OpenAI 的文档](https://platform.openai.com/docs/guides/chat) 作为使用参考。它在帐户之间进行对话，以确保在帐户数量过多的情况下不会达到速率限制。

</summary>

## 速率限制
- 代理服务器：5 请求/秒
- OpenAI：60 请求/小时（每个账户）

## 配置

1. 在OpenAI的 [ChatGPT 网站](https://chat.openai.com/)创建账户
2. 记住你的邮箱地址与密码

### 身份验证方式: (任选其一)

#### - 邮箱/密码 登录
不支持使用 Google/Microsoft 账号 授权登录的账户
```json
{
  "email": "email",
  "password": "your password"
}
```

#### - 访问令牌（Access Token）验证

> 建议使用该方式验证！

https://chat.openai.com/api/auth/session

```json
{
  "access_token": "<access_token>"
}
```

#### - 可选配置内容：

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
默认情况下，数据收集&分析处于禁用状态。将`collect_analytics`设置为`true`以启用它。

3. 另存为 `$HOME/.config/revChatGPT/config.json`
4. 如果您使用的是 Windows，则需要创建一个名为`HOME`的环境变量，并将其设置为您的主配置文件，以便脚本能够找到 config.json 文件。

## 使用方法

### 命令行程序

```
python3 -m revChatGPT.V1
```

```
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT

Type '!help' to show a full list of commands

Logging in...

You:
(Press Esc followed by Enter to finish)
```

命令行界面支持多行输入，并允许使用箭头键进行导航。此外，您还可以在提示为空时通过箭头键编辑历史记录输入。如果找到匹配的先前提示，它也会完成您的输入。要完成输入，请按`Esc`，然后按`Enter`，因为仅`Enter`本身用于在多行模式下创建新行。

设置环境变量`NO_COLOR`为`true`可以禁用带色彩的命令行输出


### 开发人员的API

#### 基础开发（命令行程序）:
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

#### 基础示例 (对话流):

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

#### 基础示例 (获取返回值):

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
#### 所有的API方法
请移步 [wiki](https://github.com/acheong08/ChatGPT/wiki/) 以了解高级的开发者功能

</details>


<details>

<summary>

# V3 官方API
> 最近由OpenAI发布
> - 付费账户

</summary>

从 https://platform.openai.com/account/api-keys 获取API-key

## 命令行程序
```
python3 -m revChatGPT.V3 --api_key <api_key>
```

```
 $ python3 -m revChatGPT.V3 -h

    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT

Type '!help' to show a full list of commands
Press Esc followed by Enter or Alt+Enter to send a message.

usage: V3.py [-h] --api_key API_KEY [--temperature TEMPERATURE] [--no_stream]
             [--base_prompt BASE_PROMPT] [--proxy PROXY] [--top_p TOP_P]
             [--reply_count REPLY_COUNT] [--enable_internet] [--config CONFIG]
             [--submit_key SUBMIT_KEY]
             [--model {gpt-3.5-turbo,gpt-4,gpt-4-32k}]

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
  --model {gpt-3.5-turbo,gpt-4,gpt-4-32k}
```

## 开发API

### 基础示例
```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
chatbot.ask("Hello world")
```

### 命令行程序
```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
for data in chatbot.ask_stream("Hello world"):
    print(data, end="", flush=True)
```

</details>

# 贼好用的ChatGPT工具

[我的列表](https://github.com/stars/acheong08/lists/awesome-chatgpt)

如果要将很酷的项目添加到列表中，请提出issue

# 免责声明

这不是OpenAI官方的产品，这仅仅是我个人的项目，与OpenAI没有任何关系，不要以任何理由起诉我。


## 贡献

感谢所有为本项目做出贡献的开发者们

<a href="https://github.com/acheong08/ChatGPT/graphs/contributors">
<img src="https://contrib.rocks/image?repo=acheong08/ChatGPT" />
</a>

## 附加说明

- 一边写代码一边听由 [virtualharby](https://www.youtube.com/@virtualharby) 写的[无与伦比的歌曲](https://www.youtube.com/watch?v=VaMR_xDhsGg)

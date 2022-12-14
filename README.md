# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>
[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![PyPi](https://img.shields.io/pypi/dm/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT by OpenAI. Extensible for chatbots etc.

<sup>Connect with me on [Linkedin](https://www.linkedin.com/in/acheong08/) to support this project. I'm graduating high school soon and knowing some people might help my chances at finding employment.</sup>

# Notice 
> ### On the 12th of December 2022, OpenAI added Cloudflare protections to their API. Please refer to the new [wiki](https://github.com/acheong08/ChatGPT/wiki/Setup) for instructions
> > ### As of 13th of December 2022, a usable bypass has been made. Please update your versions as soon as possible. 
> > > ### 14th of December 2022: The maintainer is sick. Updates will be slow. Pull requests will still be reviewed

# Usage
## Installation
`pip3 install --upgrade revChatGPT`
`python3 -m playwright install`
## Usage
python3 -m revChatGPT
## Configuration (Optional)
All of these are optional
```json
{
  "session_token": "<token>",
  "proxy":"<proxy>",
  "accept_language": "en-US,en"
}
```
## Developer usage
Take a look at the [`main.py`](https://github.com/acheong08/ChatGPT/blob/main/src/revChatGPT/__main__.py)
### Basics
```python
from revChatGPT.revChatGPT import Chatbot

# Do some config
...

chatbot = Chatbot({
   # This could be blank but the dict should be here
})

chatbot.get_chat_response(prompt, output="text") #output=stream uses async generator
```
### Using a proxy?
> 连接代理后运行，等待首次浏览器自动关闭后，立即关闭代理，建议设置全局代理运行。如果顺利完成，等待浏览器第二次自动打开后。将会正确获取到参数。

> Open the proxy first, run it, wait for the browser to close automatically for the first time, and immediately close the proxy. It is recommended to set a global shortcut key to press. If completed successfully, the browser will automatically open after the second time. The parameters can be obtained correctly.

# Awesome ChatGPT
[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers
This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

# Credits
- [rawandahmad698](https://github.com/rawandahmad698) - Reverse engineering Auth0
- [FlorianREGAZ](https://github.com/FlorianREGAZ) - TLS client
- [PyRo1121](https://github.com/PyRo1121) - Linting
- [Harry-Jing](https://github.com/Harry-Jing) - Async support
- [Ukenn2112](https://github.com/Ukenn2112) - Documentation
- [aliferouss19](https://github.com/aliferouss19) - Logo
- [All other contributors](https://github.com/acheong08/ChatGPT/graphs/contributors)

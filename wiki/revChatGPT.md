
<a id="revChatGPT.Official"></a>

# revChatGPT.Official

A simple wrapper for the official ChatGPT API

<a id="revChatGPT.Official.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

Official ChatGPT API

<a id="revChatGPT.Official.Chatbot.__init__"></a>

#### \_\_init\_\_

```python
def __init__(api_key: str) -> None
```

Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)

<a id="revChatGPT.Official.Chatbot.ask"></a>

#### ask

```python
def ask(user_request: str) -> dict
```

Send a request to ChatGPT and return the response
```json
{
    "id": "...",
    "object": "text_completion",
    "created": <time>,
    "model": "text-chat-davinci-002-20230126",
    "choices": [
        {
        "text": "<Response here>",
        "index": 0,
        "logprobs": null,
        "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
        }
    ],
    "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
}
```

<a id="revChatGPT.Official.Chatbot.rollback"></a>

#### rollback

```python
def rollback(num: int) -> None
```

Rollback chat history num times

<a id="revChatGPT.Official.Chatbot.reset"></a>

#### reset

```python
def reset() -> None
```

Reset chat history
<a id="revChatGPT"></a>

# revChatGPT

<a id="revChatGPT.GPTserver"></a>

# revChatGPT.GPTserver

<a id="revChatGPT.GPTserver.verify_data"></a>

#### verify\_data

```python
def verify_data(data: dict) -> bool
```

Verifies that the required fields are present in the data.

<a id="revChatGPT.GPTserver.chat"></a>

#### chat

```python
@app.route("/chat", methods=["POST"])
def chat()
```

The main chat endpoint.

<a id="revChatGPT.GPTserver.refresh"></a>

#### refresh

```python
@app.route("/refresh", methods=["POST"])
def refresh()
```

The refresh endpoint.

<a id="revChatGPT.ChatGPT"></a>

# revChatGPT.ChatGPT

<a id="revChatGPT.ChatGPT.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

<a id="revChatGPT.ChatGPT.Chatbot.reset_chat"></a>

#### reset\_chat

```python
def reset_chat() -> None
```

Reset the conversation ID and parent ID.

**Returns**:

None

<a id="revChatGPT.ChatGPT.Chatbot.microsoft_login"></a>

#### microsoft\_login

```python
def microsoft_login() -> None
```

Login to OpenAI via Microsoft Login Authentication.

**Returns**:

None

<a id="revChatGPT.ChatGPT.Chatbot.solve_captcha"></a>

#### solve\_captcha

```python
def solve_captcha() -> str
```

Solve the 2Captcha captcha.

**Returns**:

str

<a id="revChatGPT.ChatGPT.Chatbot.email_login"></a>

#### email\_login

```python
def email_login(solved_captcha) -> None
```

Login to OpenAI via Email/Password Authentication and 2Captcha.

**Returns**:

None

<a id="revChatGPT.ChatGPT.Chatbot.get_cf_cookies"></a>

#### get\_cf\_cookies

```python
def get_cf_cookies() -> None
```

Get cloudflare cookies.

**Returns**:

None

<a id="revChatGPT.ChatGPT.Chatbot.rollback_conversation"></a>

#### rollback\_conversation

```python
def rollback_conversation(num=1) -> None
```

Rollback the conversation.

**Arguments**:

- `num`: The number of messages to rollback

**Returns**:

None

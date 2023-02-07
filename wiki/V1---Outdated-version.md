<a id="revChatGPT.Unofficial"></a>

# revChatGPT.Unofficial

<a id="revChatGPT.Unofficial.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

<a id="revChatGPT.Unofficial.Chatbot.reset_chat"></a>

#### reset\_chat

```python
def reset_chat() -> None
```

Reset the conversation ID and parent ID.

**Returns**:

None

<a id="revChatGPT.Unofficial.Chatbot.microsoft_login"></a>

#### microsoft\_login

```python
def microsoft_login() -> None
```

Login to OpenAI via Microsoft Login Authentication.

**Returns**:

None

<a id="revChatGPT.Unofficial.Chatbot.solve_captcha"></a>

#### solve\_captcha

```python
def solve_captcha() -> str
```

Solve the 2Captcha captcha.

**Returns**:

str

<a id="revChatGPT.Unofficial.Chatbot.email_login"></a>

#### email\_login

```python
def email_login(solved_captcha) -> None
```

Login to OpenAI via Email/Password Authentication and 2Captcha.

**Returns**:

None

<a id="revChatGPT.Unofficial.Chatbot.get_cf_cookies"></a>

#### get\_cf\_cookies

```python
def get_cf_cookies() -> None
```

Get cloudflare cookies.

**Returns**:

None

<a id="revChatGPT.Unofficial.Chatbot.rollback_conversation"></a>

#### rollback\_conversation

```python
def rollback_conversation(num=1) -> None
```

Rollback the conversation.

**Arguments**:

- `num`: The number of messages to rollback

**Returns**:

None

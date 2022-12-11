<a id="revChatGPT"></a>

# revChatGPT

<a id="revChatGPT.Exceptions"></a>

# revChatGPT.Exceptions

<a id="revChatGPT.__main__"></a>

# revChatGPT.\_\_main\_\_

<a id="revChatGPT.__main__.CaptchaSolver"></a>

## CaptchaSolver Objects

```python
class CaptchaSolver()
```

Captcha solver

<a id="revChatGPT.__main__.CaptchaSolver.solve_captcha"></a>

#### solve\_captcha

```python
@staticmethod
def solve_captcha(raw_svg)
```

Solves the captcha

**Arguments**:

- `raw_svg` (`:obj:`str``): The raw SVG

**Returns**:

`:obj:`str``: The solution

<a id="revChatGPT.revChatGPT"></a>

# revChatGPT.revChatGPT

<a id="revChatGPT.revChatGPT.generate_uuid"></a>

#### generate\_uuid

```python
def generate_uuid() -> str
```

Generate a UUID for the session -- Internal use only

**Returns**:

`:obj:`str``: a random UUID

<a id="revChatGPT.revChatGPT.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

Initialize the chatbot.

See wiki for the configuration json:
https://github.com/acheong08/ChatGPT/wiki/Setup

**Arguments**:

- `config` (`:obj:`json``): The configuration json
- `conversation_id` (`:obj:`str`, optional`): The conversation ID
- `parent_id` (`:obj:`str`, optional`): The parent ID
- `debug` (`:obj:`bool`, optional`): Whether to enable debug mode
- `refresh` (`:obj:`bool`, optional`): Whether to refresh the session
- `request_timeout` (`:obj:`int`, optional`): The network request timeout seconds

**Returns**:

`:obj:`Chatbot``: The Chatbot object

<a id="revChatGPT.revChatGPT.Chatbot.reset_chat"></a>

#### reset\_chat

```python
def reset_chat() -> None
```

Reset the conversation ID and parent ID.

**Returns**:

None

<a id="revChatGPT.revChatGPT.Chatbot.get_chat_response"></a>

#### get\_chat\_response

```python
def get_chat_response(prompt: str, output="text") -> dict or None
```

Get the chat response.

**Arguments**:

- `prompt` (`:obj:`str``): The message sent to the chatbot
- `output` (`:obj:`str`, optional`): The output type `text` or `stream`

**Returns**:

`:obj:`dict` or :obj:`None``: The chat response `{"message": "Returned messages", "conversation_id": "conversation ID", "parent_id": "parent ID"}` or None

<a id="revChatGPT.revChatGPT.Chatbot.rollback_conversation"></a>

#### rollback\_conversation

```python
def rollback_conversation() -> None
```

Rollback the conversation.

**Returns**:

None

<a id="revChatGPT.revChatGPT.Chatbot.refresh_session"></a>

#### refresh\_session

```python
def refresh_session() -> None
```

Refresh the session.

**Returns**:

None

<a id="revChatGPT.revChatGPT.Chatbot.login"></a>

#### login

```python
def login(email: str, password: str) -> None
```

Log in to OpenAI.

**Arguments**:

- `email` (`:obj:`str``): The email
- `password` (`:obj:`str``): The password

**Returns**:

None

<a id="revChatGPT.revChatGPT.AsyncChatBot"></a>

## AsyncChatBot Objects

```python
class AsyncChatBot(Chatbot)
```

<a id="revChatGPT.revChatGPT.AsyncChatBot.get_chat_response"></a>

#### get\_chat\_response

```python
async def get_chat_response(prompt: str, output="text") -> dict or None
```

Get the chat response.

**Arguments**:

- `prompt` (`:obj:`str``): The message sent to the chatbot
- `output` (`:obj:`str`, optional`): The output type `text` or `stream`

**Returns**:

`:obj:`dict` or :obj:`None``: The chat response `{"message": "Returned messages", "conversation_id": "conversation ID", "parent_id": "parent ID"}` or None

<a id="revChatGPT.revChatGPT.AsyncChatBot.rollback_conversation"></a>

#### rollback\_conversation

```python
def rollback_conversation() -> None
```

Rollback the conversation.

**Returns**:

None


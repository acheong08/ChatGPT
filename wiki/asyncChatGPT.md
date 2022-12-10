<a id="asyncChatGPT"></a>

# asyncChatGPT

<a id="asyncChatGPT.asyncChatGPT"></a>

# asyncChatGPT.asyncChatGPT

<a id="asyncChatGPT.asyncChatGPT.generate_uuid"></a>

#### generate\_uuid

```python
def generate_uuid() -> str
```

Generate a UUID for the session -- Internal use only

**Returns**:

`uid` (:obj:`str`): A random UUID

<a id="asyncChatGPT.asyncChatGPT.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot(config, conversation_id=None, parent_id=None, debug=False, refresh=True, request_timeout=100, captcha_solver=None)
```

Initialize the chatbot.

See wiki for the configuration json:
https://github.com/acheong08/ChatGPT/wiki/Setup

**Arguments**:

- `config` (:obj:`json`): The configuration json
- `conversation_id` (:obj:`str`, `optional`): The conversation ID
- `parent_id` (:obj:`str`, `optional`): The parent ID
- `debug` (:obj:`bool`, `optional`): Whether to enable debug mode
- `refresh` (:obj:`bool`, `optional`): Whether to refresh the session
- `request_timeout` (:obj:`int`, `optional`): The network request timeout in seconds
- `captcha_solver` (:obj:`any`, `optional`): The `CaptchaSolver()` object

**Returns**:

`Chatbot` (:obj:`Chatbot`): The chatbot object

<a id="asyncChatGPT.asyncChatGPT.Chatbot.reset_chat"></a>

#### reset\_chat

```python
def reset_chat() -> None
```

Reset the conversation ID and parent ID.

**Returns**:

None

<a id="asyncChatGPT.asyncChatGPT.Chatbot.__refresh_headers"></a>

#### refresh\_headers

```python
def __refresh_headers() -> None
```

Refresh the headers -- Internal use only

**Returns**:

None

<a id="asyncChatGPT.asyncChatGPT.Chatbot.get_chat_response"></a>

#### get\_chat\_response

```python
async def get_chat_response(prompt: str, output="text") -> dict or None
```

Get the chat response.

**Arguments**:

- `prompt` (:obj:`str`): The message sent to the chatbot
- `output` (:obj:`str`, `optional`): The type of the output (`"text"` or `"stream"`)

**Returns**:

The chat response (:obj:`dict`):

```python
{"message": returned messages (:obj:`str`), 
 "conversation_id": conversation ID (:obj:`str`),
 "parent_id": parent ID (:obj:`str`)}
``` 

or None

<a id="asyncChatGPT.asyncChatGPT.Chatbot.rollback_conversation"></a>

#### rollback\_conversation

```python
def rollback_conversation() -> None
```

Rollback the conversation.

**Returns**:

None

<a id="asyncChatGPT.asyncChatGPT.Chatbot.refresh_session"></a>

#### refresh\_session

```python
def refresh_session() -> None
```

Refresh the session.

**Returns**:

None

<a id="asyncChatGPT.asyncChatGPT.Chatbot.login"></a>

#### login

```python
def login(email: str, password: str) -> None
```

Log in to OpenAI.

**Arguments**:

- `email` (:obj:`str`): The email
- `password` (:obj:`str`): The password

**Returns**:

None


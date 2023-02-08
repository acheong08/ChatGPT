<a id="revChatGPT.Unofficial"></a>

# revChatGPT.Unofficial

<a id="revChatGPT.Unofficial.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

<a id="revChatGPT.Unofficial.Chatbot.ask"></a>

#### ask

```python
def ask(prompt,
        conversation_id=None,
        parent_id=None,
        gen_title=False,
        session_token=None)
```

Ask a question to the chatbot

**Arguments**:

- `prompt`: String
- `conversation_id`: UUID
- `parent_id`: UUID
- `gen_title`: Boolean
- `session_token`: String

<a id="revChatGPT.Unofficial.Chatbot.get_conversations"></a>

#### get\_conversations

```python
def get_conversations(offset=0, limit=20)
```

Get conversations

**Arguments**:

- `offset`: Integer
- `limit`: Integer

<a id="revChatGPT.Unofficial.Chatbot.get_msg_history"></a>

#### get\_msg\_history

```python
def get_msg_history(id)
```

Get message history

**Arguments**:

- `id`: UUID of conversation

<a id="revChatGPT.Unofficial.Chatbot.change_title"></a>

#### change\_title

```python
def change_title(id, title)
```

Change title of conversation

**Arguments**:

- `id`: UUID of conversation
- `title`: String

<a id="revChatGPT.Unofficial.Chatbot.delete_conversation"></a>

#### delete\_conversation

```python
def delete_conversation(id)
```

Delete conversation

**Arguments**:

- `id`: UUID of conversation

<a id="revChatGPT.Unofficial.Chatbot.clear_conversations"></a>

#### clear\_conversations

```python
def clear_conversations()
```

Delete all conversations

<a id="revChatGPT.Unofficial.Chatbot.reset_chat"></a>

#### reset\_chat

```python
def reset_chat() -> None
```

Reset the conversation ID and parent ID.

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

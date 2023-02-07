<a id="revChatGPT.Official"></a>

# revChatGPT.Official

A simple wrapper for the official ChatGPT API

<a id="revChatGPT.Official.get_max_tokens"></a>

#### get\_max\_tokens

```python
def get_max_tokens(prompt: str) -> int
```

Get the max tokens for a prompt

<a id="revChatGPT.Official.remove_suffix"></a>

#### remove\_suffix

```python
def remove_suffix(input_string, suffix)
```

Remove suffix from string (Support for Python 3.8)

<a id="revChatGPT.Official.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

Official ChatGPT API

<a id="revChatGPT.Official.Chatbot.__init__"></a>

#### \_\_init\_\_

```python
def __init__(api_key: str, buffer: int = None, engine: str = None) -> None
```

Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)

<a id="revChatGPT.Official.Chatbot.ask"></a>

#### ask

```python
def ask(user_request: str,
        temperature: float = 0.5,
        conversation_id: str = None,
        user: str = "User") -> dict
```

Send a request to ChatGPT and return the response

<a id="revChatGPT.Official.Chatbot.ask_stream"></a>

#### ask\_stream

```python
def ask_stream(user_request: str,
               temperature: float = 0.5,
               conversation_id: str = None,
               user: str = "User") -> str
```

Send a request to ChatGPT and yield the response

<a id="revChatGPT.Official.Chatbot.make_conversation"></a>

#### make\_conversation

```python
def make_conversation(conversation_id: str) -> None
```

Make a conversation

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

<a id="revChatGPT.Official.Chatbot.load_conversation"></a>

#### load\_conversation

```python
def load_conversation(conversation_id) -> None
```

Load a conversation from the conversation history

<a id="revChatGPT.Official.Chatbot.save_conversation"></a>

#### save\_conversation

```python
def save_conversation(conversation_id) -> None
```

Save a conversation to the conversation history

<a id="revChatGPT.Official.AsyncChatbot"></a>

## AsyncChatbot Objects

```python
class AsyncChatbot(Chatbot)
```

Official ChatGPT API (async)

<a id="revChatGPT.Official.AsyncChatbot.ask"></a>

#### ask

```python
async def ask(user_request: str,
              temperature: float = 0.5,
              user: str = "User") -> dict
```

Same as Chatbot.ask but async
}

<a id="revChatGPT.Official.AsyncChatbot.ask_stream"></a>

#### ask\_stream

```python
async def ask_stream(user_request: str,
                     temperature: float = 0.5,
                     user: str = "User") -> str
```

Same as Chatbot.ask_stream but async

<a id="revChatGPT.Official.Prompt"></a>

## Prompt Objects

```python
class Prompt()
```

Prompt class with methods to construct prompt

<a id="revChatGPT.Official.Prompt.__init__"></a>

#### \_\_init\_\_

```python
def __init__(buffer: int = None) -> None
```

Initialize prompt with base prompt

<a id="revChatGPT.Official.Prompt.add_to_chat_history"></a>

#### add\_to\_chat\_history

```python
def add_to_chat_history(chat: str) -> None
```

Add chat to chat history for next prompt

<a id="revChatGPT.Official.Prompt.add_to_history"></a>

#### add\_to\_history

```python
def add_to_history(user_request: str,
                   response: str,
                   user: str = "User") -> None
```

Add request/response to chat history for next prompt

<a id="revChatGPT.Official.Prompt.history"></a>

#### history

```python
def history(custom_history: list = None) -> str
```

Return chat history

<a id="revChatGPT.Official.Prompt.construct_prompt"></a>

#### construct\_prompt

```python
def construct_prompt(new_prompt: str,
                     custom_history: list = None,
                     user: str = "User") -> str
```

Construct prompt based on chat history and request

<a id="revChatGPT.Official.Conversation"></a>

## Conversation Objects

```python
class Conversation()
```

For handling multiple conversations

<a id="revChatGPT.Official.Conversation.add_conversation"></a>

#### add\_conversation

```python
def add_conversation(key: str, history: list) -> None
```

Adds a history list to the conversations dict with the id as the key

<a id="revChatGPT.Official.Conversation.get_conversation"></a>

#### get\_conversation

```python
def get_conversation(key: str) -> list
```

Retrieves the history list from the conversations dict with the id as the key

<a id="revChatGPT.Official.Conversation.remove_conversation"></a>

#### remove\_conversation

```python
def remove_conversation(key: str) -> None
```

Removes the history list from the conversations dict with the id as the key

<a id="revChatGPT.Official.Conversation.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Creates a JSON string of the conversations

<a id="revChatGPT.Official.Conversation.save"></a>

#### save

```python
def save(file: str) -> None
```

Saves the conversations to a JSON file

<a id="revChatGPT.Official.Conversation.load"></a>

#### load

```python
def load(file: str) -> None
```

Loads the conversations from a JSON file

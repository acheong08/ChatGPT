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
Response: {
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

<a id="revChatGPT.Official.Chatbot.ask_stream"></a>

#### ask\_stream

```python
def ask_stream(user_request: str) -> str
```

Send a request to ChatGPT and yield the response

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

<a id="revChatGPT.Official.Chatbot.save_conversation"></a>

#### save\_conversation

```python
def save_conversation(conversation_id: str) -> None
```

Save conversation to conversations dict

<a id="revChatGPT.Official.Chatbot.load_conversation"></a>

#### load\_conversation

```python
def load_conversation(conversation_id: str) -> None
```

Load conversation from conversations dict

<a id="revChatGPT.Official.Chatbot.delete_conversation"></a>

#### delete\_conversation

```python
def delete_conversation(conversation_id: str) -> None
```

Delete conversation from conversations dict

<a id="revChatGPT.Official.Chatbot.get_conversations"></a>

#### get\_conversations

```python
def get_conversations() -> dict
```

Get all conversations

<a id="revChatGPT.Official.Chatbot.dump_conversation_history"></a>

#### dump\_conversation\_history

```python
def dump_conversation_history() -> None
```

Save all conversations history to a json file

<a id="revChatGPT.Official.Chatbot.load_conversation_history"></a>

#### load\_conversation\_history

```python
def load_conversation_history() -> None
```

Load conversation history from json files

<a id="revChatGPT.Official.AsyncChatbot"></a>

## AsyncChatbot Objects

```python
class AsyncChatbot(Chatbot)
```

Official ChatGPT API (async)

<a id="revChatGPT.Official.AsyncChatbot.ask"></a>

#### ask

```python
async def ask(user_request: str) -> dict
```

Send a request to ChatGPT and return the response
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

<a id="revChatGPT.Official.AsyncChatbot.ask_stream"></a>

#### ask\_stream

```python
async def ask_stream(user_request: str) -> dict
```

Send a request to ChatGPT and yield the response

<a id="revChatGPT.Official.Prompt"></a>

## Prompt Objects

```python
class Prompt()
```

Prompt class with methods to construct prompt

<a id="revChatGPT.Official.Prompt.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

Initialize prompt with base prompt

<a id="revChatGPT.Official.Prompt.add_to_chat_history"></a>

#### add\_to\_chat\_history

```python
def add_to_chat_history(chat: str) -> None
```

Add chat to chat history for next prompt

<a id="revChatGPT.Official.Prompt.history"></a>

#### history

```python
def history() -> str
```

Return chat history

<a id="revChatGPT.Official.Prompt.construct_prompt"></a>

#### construct\_prompt

```python
def construct_prompt(new_prompt: str) -> str
```

Construct prompt based on chat history and request

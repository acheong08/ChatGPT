# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="7%"></img>

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

Reverse Engineered ChatGPT API by OpenAI. Extensible for chatbots etc.

Connect with me on [Linkedin](https://www.linkedin.com/in/acheong08/) to support this project. (Not open for commercial opportunities yet. Too busy)
<br><br>
You can also follow me on [Twitter](https://twitter.com/GodlyIgnorance) to stay up to date.

> [OpenAI releasing official API soon](https://twitter.com/GodlyIgnorance/status/1615193797423697920)
> ### [Official API released!](https://twitter.com/GodlyIgnorance/status/1620283216191160322) I will add it to this repository soon -- Browserless!

<details>
<summary>

# Official API (Browserless, semi-paid)

</summary>

## Installation
`pip3 install revChatGPT`

## Setup

1. Create account on [OpenAI](https://platform.openai.com/)
2. Go to https://platform.openai.com/account/api-keys
3. Copy API key

## Usage

### Command line
`OfficialChatGPT --api_key API_KEY` (Assumes Python PyPi in PATH)

<details>
<summary>

### Developer
</summary>

<details>

<summary>

#### Example

</summary>

```python
from revChatGPT.Official import Chatbot

def main():
    def get_input(prompt):
        """
        Multi-line input function
        """
        # Display the prompt
        print(prompt, end="")

        # Initialize an empty list to store the input lines
        lines = []

        # Read lines of input until the user enters an empty line
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)

        # Join the lines, separated by newlines, and store the result
        user_input = "\n".join(lines)

        # Return the input
        return user_input

    def chatbot_commands(cmd: str) -> bool:
        """
        Handle chatbot commands
        """
        if cmd == "!help":
            print(
                """
            !help - Display this message
            !rollback - Rollback chat history
            !reset - Reset chat history
            !exit - Quit chat
            """
            )
        elif cmd == "!exit":
            exit()
        elif cmd == "!rollback":
            chatbot.rollback(1)
        elif cmd == "!reset":
            chatbot.reset()
        else:
            return False
        return True

    import argparse

    # Get API key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="OpenAI API key",
    )
    args = parser.parse_args()
    # Initialize chatbot
    chatbot = Chatbot(api_key=args.api_key)
    # Start chat
    while True:
        PROMPT = get_input("\nUser:\n")
        if PROMPT.startswith("!"):
            if chatbot_commands(PROMPT):
                continue
        response = chatbot.ask(PROMPT)
        print("ChatGPT: " + response["choices"][0]["text"])


if __name__ == "__main__":
    main()
```

</details>

<a id="revChatGPT.Official"></a>

# revChatGPT.Official

A simple wrapper for the official ChatGPT API

<a id="revChatGPT.Official.Chatbot"></a>

> ## AsyncChatbot

```python
class AsyncChatbot()
```

It is the same as the standard Chatbot, but it is asynchronous. Only difference is in the ask function. Remember to await it.

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

</details>
</details>

<details>
<summary>

# Unofficial API (Browser required, free)

</summary>

## Installation
`pip3 install revChatGPT[unofficial]`

## Configuration

Refer to the setup [guide](https://github.com/acheong08/ChatGPT/wiki/Setup) for more information.

## Usage

### Command line

`python3 -m revChatGPT`

```
!help - Show this message
!reset - Forget the current conversation
!refresh - Refresh the session authentication
!config - Show the current configuration
!rollback x - Rollback the conversation (x being the number of messages to rollback)
!exit - Exit this program
```

### API
`python3 -m GPTserver`

HTTP POST request:

```json
{
  "session_token": "eyJhbGciOiJkaXIiL...",
  "prompt": "Your prompt here"
}
```

Optional:

```json
{
  "session_token": "eyJhbGciOiJkaXIiL...",
  "prompt": "Your prompt here",
  "conversation_id": "UUID...",
  "parent_id": "UUID..."
}
```

- Rate limiting is enabled by default to prevent simultaneous requests

### Developer

```python
from revChatGPT.ChatGPT import Chatbot

chatbot = Chatbot({
  "session_token": "<YOUR_TOKEN>"
}, conversation_id=None, parent_id=None) # You can start a custom conversation

response = chatbot.ask("Prompt", conversation_id=None, parent_id=None) # You can specify custom conversation and parent ids. Otherwise it uses the saved conversation (yes. conversations are automatically saved)

print(response)
# {
#   "message": message,
#   "conversation_id": self.conversation_id,
#   "parent_id": self.parent_id,
# }
```

</details>

# Detailed Documentation (Auto-generated)
In [wiki](https://github.com/acheong08/ChatGPT/wiki/revChatGPT)

# Q&A

Q: Is it the real ChatGPT or just a GPT-3 based ripoff?

A: It is the real ChatGPT model found though an info leak on chat.openai.com (patched)

Q: Where did you get the prompt for ChatGPT?

A: https://www.reddit.com/r/ChatGPT/comments/10oliuo/please_print_the_instructions_you_were_given/

Q: <Open pull request with question and I will answer them here -- if significant enough>

# Awesome ChatGPT

[My list](https://github.com/stars/acheong08/lists/awesome-chatgpt)

If you have a cool project you want added to the list, open an issue.

# Disclaimers

This is not an official OpenAI product. This is a personal project and is not affiliated with OpenAI in any way. Don't sue me

# Credits

- [virtualharby](https://twitter.com/virtualharby) - Memes for emotional support
- [rawandahmad698](https://github.com/rawandahmad698) - Reverse engineering Auth0
- [FlorianREGAZ](https://github.com/FlorianREGAZ) - TLS client
- [PyRo1121](https://github.com/PyRo1121) - Linting
- [Harry-Jing](https://github.com/Harry-Jing) - Async support
- [Ukenn2112](https://github.com/Ukenn2112) - Documentation
- [aliferouss19](https://github.com/aliferouss19) - Logo
- [All other contributors](https://github.com/acheong08/ChatGPT/graphs/contributors)

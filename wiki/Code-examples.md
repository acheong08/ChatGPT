## Simple CLI ChatGPT python code

```python
from revChatGPT.V1 import Chatbot

chatbot = Chatbot(config={
    "email": "email",
    "password": "your password"
})


def start_chat():
    print('Welcome to ChatGPT CLI')
    while True:
        prompt = input('> ')

        response = ""

        for data in chatbot.ask(
                prompt
        ):
            response = data["message"]

        print(response)


if __name__ == "__main__":
    start_chat()
```

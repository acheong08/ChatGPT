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

## A GUI ChatGPT code with tkinter

```python
import tkinter as tk
from revChatGPT.V1 import Chatbot


chatbot = Chatbot(config={
  "email": "<email>",
  "password": "<your password>"
})


def respond(event):
    if event.state == 1:
        return

    prompt = textbox.get("1.0", 'end-1c')
    response = ""

    for data in chatbot.ask(
            prompt
    ):
        response = data["message"]
    textbox.delete("1.0", 'end-1c')
    history.insert(tk.INSERT, "User: " + prompt + "\n\nChatGPT: " + response + "\n\n\n")


root = tk.Tk()
root.title("Chat App")

title = tk.Label(root, text="ChatGPT GUI", width=70, font=("Arial", 30, "bold"))
title.pack()
textbox = tk.Text(root, width=50, font=("Arial", 14), fg="white")

history = tk.Text(root, width=110, font=("Arial", 12))
history.pack(padx=10, pady=10)

textbox.pack(padx=10, pady=10)

textbox.bind("<Return>", respond)

root.configure(background="#292929")
textbox.configure(background="#39433e")
history.configure(background="#39433e", foreground="#F7C04A")
title.configure(background="#292929", foreground="#FFFFFF")
root.geometry("1100x700")
root.mainloop()

```

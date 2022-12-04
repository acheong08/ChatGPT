import ChatGPT
import json

with open("config.json", "r") as f:
    config = json.load(f)

chatbot = ChatGPT.Chatbot(config)

prompts = open("prompts.txt", "r").readlines()
for prompt in prompts:
    response = chatbot.get_chat_response(prompt)
    print(response["message"])
import revChatGPT
import json

with open("config.json", "r") as f:
    config = json.load(f)

chatbot = revChatGPT.Chatbot(config, conversation_id=None)

prompts = open("prompts.txt", "r").readlines()
for prompt in prompts:
    response = chatbot.get_chat_response(prompt)
    print(response["message"])
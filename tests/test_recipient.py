import asyncio
import json

from revChatGPT.V1 import AsyncChatbot
from revChatGPT.V1 import Chatbot

config = json.load(open("/home/acheong/.config/revChatGPT/config.json"))


async def main():
    chatbot = AsyncChatbot(config)
    async for message in chatbot.ask("Hello, how are you?"):
        print(message.get("message"))

    print(await chatbot.share_conversation())


def sync_main():
    chatbot = Chatbot(config)
    for message in chatbot.ask("Hello, how are you?"):
        print(message.get("message"))


asyncio.run(main())

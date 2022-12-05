import asyncio
import json

from revChatGPT.revChatGPT import AsyncChatbot


def get_input(prompt):
  # prompt for input
  lines = []
  print(prompt,end="")
  while True:
      line = input()
      if line == "":
          break
      lines.append(line)

  # Join the lines, separated by newlines, and print the result
  user_input = "\n".join(lines)
  #print(user_input)
  return user_input

if __name__ == "__main__":
    async def main():
        print(
            """
        ChatGPT -   command-line interface 到 OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """
        )
        print("Type '!help' to show commands")
        print("Press enter twice to submit your question.\n")
        with open("config.json", "r") as f:
            config = json.load(f)
        chatbot = AsyncChatbot(config)
        if "session_token" in config:
            await chatbot.refresh_session()

        import sys
        from subprocess import Popen

        while True:
            prompt = get_input("You: ")
            if prompt.startswith("!"):
                if prompt == "!help":
                    print(
                        """
                    !help - Show this message
                    !reset - Forget   current conversation
                    !refresh - 刷新   session authentication
                    !exit - Exit   program
                    """
                    )
                    continue
                elif prompt == "!reset":
                    chatbot.reset_chat()
                    print("Chat session reset.")
                    continue
                elif prompt == "!refresh":
                    await chatbot.refresh_session()
                    print("Session refreshed.\n")
                    # 保存   new config
                    with open("config.json", "w") as f:
                        json.dump(chatbot.config, f)
                    continue
                elif prompt == "!exit":
                    break
            try:
                print("Please wait for ChatGPT to formulate its full response...")
                response = await chatbot.get_chat_response(prompt)
            except Exception as e:
                print("Something went wrong!")
                print(e)
                continue
            # Erase   "Please wait" line when done 等待中
            sys.stdout.write("\033[F\033[K")

            print("\n")
            print("Chatbot:", response["message"])
            print("\n")

            arguments = list(sys.argv)
            del arguments[0]

            if len(arguments) > 2:
                try:
                    process.terminate()
                except NameError:
                    print("")

                # 使用 `python3 ./revChatGPT.py say -v Samantha -r 600` 到 make a Mac speak   output
                # using   Samantha voice 在 600 words per minute (about 3x)
                # 或 `python3 ./revChatGPT.py espeak -v en -s 600` 到 do something similar using espeak (untested)
                arguments.append('"' + response["message"] + '"')
                process = Popen(arguments)

    asyncio.run(main())
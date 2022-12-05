import asyncio
import json

from reprint import output

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
        print("""
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """)
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
                    !reset - Forget the current conversation
                    !refresh - Refresh the session authentication
                    !exit - Exit the program
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
                    # Save the new config
                    with open("config.json", "w") as f:
                        json.dump(chatbot.config, f)
                    continue
                elif prompt == "!exit":
                    break
            print("Please wait for ChatGPT to formulate its full response...")
            try:
                message = ""
                i = 0
                with output() as output_list:
                    async for line in chatbot.get_chat_stream_response(prompt):
                        if not message:
                            # Erase the "Please wait" line when done waiting
                            sys.stdout.write("\033[F\033[K")
                            message += "Chatbot: "
                        message += line["message"]
                        output_list[i] = message
                        if line["message"] == "\n":
                            i += 1
                            output_list.append(message := "\n")
            except Exception as e:
                print("Something went wrong!")
                print(e)
                continue

            print("\n")

            arguments = list(sys.argv)
            del arguments[0]

            if len(arguments) > 2:
                try:
                    process.terminate()
                except NameError:
                    print("")

                # Use `python3 ./revChatGPT.py say -v Samantha -r 600` to make a Mac speak the output
                # using the Samantha voice at 600 words per minute (about 3x)
                # or `python3 ./revChatGPT.py espeak -v en -s 600` to do something similar using espeak (untested)
                arguments.append('"' + "".join(output_list) + '"')
                process = Popen(arguments)

    asyncio.run(main())
import json
import textwrap
from os.path import exists
from sys import argv

from revChatGPT.revChatGPT import Chatbot


def get_input(prompt):
    # prompt for input
    lines = []
    print(prompt, end="")
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    # Join the lines, separated by newlines, and print the result
    user_input = "\n".join(lines)
    # print(user_input)
    return user_input


if __name__ == "__main__":
    try:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """,
        )
        print("Type '!help' to show commands")
        print("Press enter twice to submit your question.\n")

        if exists("config.json"):
            with open("config.json", encoding="utf-8") as f:
                config = json.load(f)
            if "--debug" in argv:
                print("Debugging enabled.")
                debug = True
            else:
                debug = False
            print("Logging in...")
            chatbot = Chatbot(config, debug=debug)
        else:
            print("Please create and populate config.json to continue")
            exit()

        while True:
            prompt = get_input("\nYou:\n")
            if prompt.startswith("!"):
                if prompt == "!help":
                    print(
                        """
                    !help - Show this message
                    !reset - Forget the current conversation
                    !refresh - Refresh the session authentication
                    !rollback - Rollback the conversation by 1 message
                    !config - Show the current configuration
                    !exit - Exit the program
                    """,
                    )
                    continue
                elif prompt == "!reset":
                    chatbot.reset_chat()
                    print("Chat session reset.")
                    continue
                elif prompt == "!refresh":
                    chatbot.refresh_session()
                    print("Session refreshed.\n")
                    continue
                elif prompt == "!rollback":
                    chatbot.rollback_conversation()
                    print("Chat session rolled back.")
                    continue
                elif prompt == "!config":
                    print(json.dumps(config, indent=4))
                    continue
                elif prompt == "!exit":
                    break

            if "--text" not in argv:
                messages = []
                lines_printed = 0

                try:
                    print("Chatbot: ")
                    formatted_parts = []
                    for message in chatbot.get_chat_response(prompt, output="stream"):
                        # Split the message by newlines
                        message_parts = message["message"].split("\n")

                        # Wrap each part separately
                        formatted_parts = []
                        for part in message_parts:
                            formatted_parts.extend(
                                textwrap.wrap(part, width=80))
                            for formatted_line in formatted_parts:
                                if len(formatted_parts) > lines_printed + 1:
                                    print(formatted_parts[lines_printed])
                                    lines_printed += 1
                    print(formatted_parts[lines_printed])
                except Exception as e:
                    print("Something went wrong!")
                    print(e)
                    continue
            else:
                try:
                    print("Chatbot: ")
                    message = chatbot.get_chat_response(prompt)
                    print(message["message"])
                except Exception as e:
                    print("Something went wrong!")
                    print(e)
                    continue
    except Exception as e:
        print("Something went wrong! Please run with --debug to see the error.")
        print(e)
        exit()

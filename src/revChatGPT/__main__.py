import json
import textwrap
from os.path import exists
from os import getenv
from sys import argv, exit

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


def configure():
    try:
        config_files = ["config.json"]
        xdg_config_home = getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
        user_home = getenv("HOME")
        if user_home:
            config_files.append(f"{user_home}/.config/revChatGPT/config.json")

        config_file = next((f for f in config_files if exists(f)), None)
        if config_file:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        else:
            print("No config file found.")
            config = {}
        if "--debug" in argv:
            print("Debugging enabled.")
            debug = True
        else:
            debug = False
        verify_config(config)
        chatGPT_main(config, debug)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit()
    except Exception as exc:
        print("Something went wrong! Please run with --debug to see the error.")
        print(exc)
        exit()


def verify_config(config):
    """
    Verifies the config

    :param config: The config
    :type config: :obj:`dict`
    """
    # Check if the config is empty
    if 'email' in config or 'password' in config:
        print("Email and passwords are no longer supported")


def chatGPT_main(config, debug):
    print("Logging in...")
    chatbot = Chatbot(config, debug=debug)
    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if prompt == "!help":
                print(
                    """
                !help - Show this message
                !reset - Forget the current conversation
                !refresh - Refresh the session authentication
                !rollback <num> - Rollback the conversation by <num> message(s); <num> is optional, defaults to 1
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
            # elif prompt == "!rollback":
            elif prompt.startswith("!rollback"):
                try:
                    # Get the number of messages to rollback
                    num = int(prompt.split(" ")[1])
                except IndexError:
                    num = 1
                chatbot.rollback_conversation(num)
                print(f"Chat session rolled back {num} message(s).")
                continue
            elif prompt == "!config":
                print(json.dumps(config, indent=4))
                continue
            elif prompt == "!exit":
                break

        if "--text" not in argv:
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
                        for _ in formatted_parts:
                            if len(formatted_parts) > lines_printed + 1:
                                print(formatted_parts[lines_printed])
                                lines_printed += 1
                print(formatted_parts[lines_printed])
            except Exception as exc:
                print("Response not in correct format!")
                print(exc)
                continue
        else:
            try:
                print("Chatbot: ")
                message = chatbot.get_chat_response(prompt)
                print(message["message"])
            except Exception as exc:
                print("Something went wrong!")
                print(exc)
                continue


def main():
    if "--help" in argv:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """,
        )
        exit()
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """,
    )
    print("Type '!help' to show commands")
    print("Press enter twice to submit your question.\n")
    configure()


if __name__ == "__main__":
    main()

import json
from os.path import exists
from os import getenv
from sys import argv, exit

from revChatGPT.ChatGPT import Chatbot


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
        raise Exception("No config file found.")
    return config


def chatGPT_main(config):
    print("Logging in...")
    chatbot = Chatbot(config)
    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if prompt == "!help":
                print(
                    """
                !help - Show this message
                !reset - Forget the current conversation
                !refresh - Refresh the session authentication
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
            elif prompt == "!config":
                print(json.dumps(chatbot.config, indent=4))
                continue
            elif prompt == "!exit":
                break
        try:
            print("Chatbot: ")
            message = chatbot.ask(prompt)
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
    chatGPT_main(configure())


if __name__ == "__main__":
    main()

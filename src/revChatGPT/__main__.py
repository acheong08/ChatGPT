import json
import textwrap
from os.path import exists
from os import getenv
from sys import argv, exit
from svglib.svglib import svg2rlg

from revChatGPT.revChatGPT import Chatbot


class CaptchaSolver:
    """
    Captcha solver
    """
    @staticmethod
    def solve_captcha(raw_svg):
        """
        Solves the captcha

        :param raw_svg: The raw SVG
        :type raw_svg: :obj:`str`

        :return: The solution
        :rtype: :obj:`str`
        """
        # Get the SVG
        svg = raw_svg
        # Save the SVG
        with open("captcha.png", "w", encoding="utf-8") as f:
            print("Captcha saved to captcha.png")
            png = svg2rlg(svg)
            f.write(png)
        # Get input
        solution = input("Please solve the captcha: ")
        # Return the solution
        return solution


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


def main():
    if "--help" in argv:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """
        )
        exit()
    try:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """
        )
        print("Type '!help' to show commands")
        print("Press enter twice to submit your question.\n")

        config_files = ["config.json"]
        xdg_config_home = getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
        user_home = getenv("HOME")
        if user_home:
            config_files.append(f"{user_home}/.config/revChatGPT/config.json")

        config_file = next((f for f in config_files if exists(f)), None)
        if not config_file:
            print("Please create and populate ./config.json, $XDG_CONFIG_HOME/revChatGPT/config.json, or ~/.config/revChatGPT/config.json to continue")
            exit()

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
        if "--debug" in argv:
            print("Debugging enabled.")
            debug = True
        else:
            debug = False
        print("Logging in...")
        chatbot = Chatbot(config, debug=debug, captcha_solver=CaptchaSolver())

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
                    """
                    )
                    continue
                elif prompt == "!reset":
                    chatbot.reset_chat()
                    print("Chat session reset.")
                    continue
                elif prompt == "!refresh":
                    chatbot.refresh_session()
                    print("Session refreshed.")
                    continue
                elif prompt == "!rollback":
                    chatbot.rollback()
                    print("Conversation rolled back.")
                    continue
                elif prompt == "!config":
                    print("Current Configuration:")
                    print(json.dumps(config, indent=2))
                    continue
                elif prompt == "!exit":
                    exit()
                else:
                    print("Unknown command")
                    continue
            response = chatbot.get_response(prompt)
            print("\nBot:\n", response)

    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()

import json
import textwrap
from os.path import exists
from os import getenv
from sys import argv, exit
from cairosvg import svg2png

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
        print("Saved captcha.png")
        svg2png(bytestring=svg, write_to="captcha.png")
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
        """,
        )
        exit()
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
        chatbot = Chatbot(config, debug=debug,
                          captcha_solver=CaptchaSolver())

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
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit()
    except Exception as exc:
        print("Something went wrong! Please run with --debug to see the error.")
        print(exc)
        exit()


if __name__ == "__main__":
    main()

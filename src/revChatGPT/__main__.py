"""
Main CLI
"""
import argparse
import sys

from . import __version__
from . import typings as t
from . import V1
from . import V3

__all__ = ()


def main():
    """
    main function for CLI
    """
    parser = argparse.ArgumentParser(
        description="ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)",
        epilog="Repo: github.com/acheong08/ChatGPT",
        allow_abbrev=True,
    )
    parser.add_argument(
        "--V1",
        action="store_true",
        help="Use the website version of ChatGPT",
    )
    parser.add_argument(
        "--V3",
        action="store_true",
        help="Use the API version of ChatGPT",
    )
    args, _ = parser.parse_known_args()
    mode = "V1" if args.V1 else "V3" if args.V3 else input("Version (V1/V3):")

    if mode == "V1":
        print(
            f"""
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Version: {__version__}
        """,
        )
        print("Type '!help' to show a full list of commands")
        print(
            f"{V1.bcolors.BOLD}{V1.bcolors.WARNING}Press Esc followed by Enter or Alt+Enter to send a message.{V1.bcolors.ENDC}",
        )
        V1.main(V1.configure())
    elif mode == "V3":
        try:
            V3.main()
        except Exception as exc:
            error = t.CLIError("Command line program unknown error")
            raise error from exc
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
    else:
        error = NotImplementedError(f"Unknown version: {mode}")
        raise error


if __name__ == "__main__":
    main()

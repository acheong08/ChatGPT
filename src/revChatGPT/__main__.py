from . import V1, V3
from . import typing as t
import sys

__all__ = ()

def main():
    if sys.argv[1].replace("--", "") in ["V1", "V3"]:
        mode = sys.argv[1].replace("--", "")
        sys.argv.remove(sys.argv[0])
    elif sys.argv[-1].replace("--", "") in ["V1", "V3"]:
        mode = sys.argv[-1].replace("--", "")
        sys.argv.remove(sys.argv[-1])
    else:
        mode = input("Please choose the version you want to use:\nV0, V1, V3\n")

    if mode == "V1":
        print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
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
        except Exception as e:
            error = t.CLIError("Command line program unknown error")
            raise error from e
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
    else:
        error = NotImplementedError(f"Unknown version: {mode}")
        raise error

if __name__ == "__main__":
    main()
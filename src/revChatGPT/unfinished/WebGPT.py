import json
import logging
import sys
import time
from typing import NoReturn

import revChatGPT.V1 as V1
from duckduckgo_search import ddg

# V1 and Unofficial are unnecessary, imo

# V2 is reportedly "killed by openai"
# V3 has own implementation

log = logging.getLogger(__name__)


def _prepare_results(results: list) -> str:
    return "".join(
        f'[{i}] "{result["body"]}"\nURL: {result["href"]}\n\n'
        for i, result in enumerate(results, start=1)
    )


def _headers(results: list) -> list:
    return [(result["href"], result["title"]) for result in results]


def _compile_prompt(prompt: str, results: list, reply_in: str = "undefined") -> str:
    return f"""Web search results:

{_prepare_results(results)}
Current date: {time.strftime("%d.%m.%Y")}

Instructions: Using the provided web search results, write a comprehensive reply to the given query, using search results as references. Make sure to cite results using [number](url) notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.
Query: {prompt}
Reply in {reply_in}"""


def webify(
    text: str,
    query: str,
    numResults: int,
    timePeriod: str = "",
    region: str = "",
    reply_in: str = "undefined",
) -> tuple[str, list]:
    """
    Returns a tuple of (prompt, headers)
    """
    searchResults = ddg(query, numResults, timePeriod, region)
    return _compile_prompt(text, searchResults, reply_in), _headers(searchResults)


def beatifyMarkdown(response: str, headers: list) -> str:
    """
    If the result will be displayed with markdown support, turns [i] style references into [i](url), which will look as clickable [i]
    If you are using beatifyPlaintext too, use this first
    """
    for i in range(len(headers)):
        response = response.replace(f"[{i+1}]", f"[{i+1}]({headers[i][0]})")
    return response


def beatifyPlaintext(response: str, headers: list) -> str:
    """
    Puts the references at the end of the response. Can be used after beatifyMarkdown. Useful for displaying result in plaintext
    """
    refs = "\n"
    for i in range(len(headers)):
        refs += f"\n[{i+1}] - {headers[i][1]} ({headers[i][0]})"
    return response + refs


class WebChatbot(V1.Chatbot):
    def webAsk(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Keep in mind: this one, unlike all the other asks, returns tuple
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        for data in self.ask(prompt, conversation_id, parent_id, timeout):
            yield data, headers

    def webAskPlaintext(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Returns message adapted for plaintext
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        for data in self.ask(prompt, conversation_id, parent_id, timeout):
            data["message"] = beatifyPlaintext(data["message"], headers)
            yield data

    def webAskMarkdown(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Returns message adapted for markdown
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        for data in self.ask(prompt, conversation_id, parent_id, timeout):
            data["message"] = beatifyMarkdown(data["message"], headers)
            yield data


class WebAsyncChatbot(V1.AsyncChatbot):
    async def webAsk(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Keep in mind: this one, unlike all the other asks, returns tuple
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        async for data in self.ask(prompt, conversation_id, parent_id, timeout):
            yield data, headers

    async def webAskPlaintext(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Returns message adapted for plaintext
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        async for data in self.ask(prompt, conversation_id, parent_id, timeout):
            data["message"] = beatifyPlaintext(data["message"], headers)
            yield data

    async def webAskMarkdown(
        self,
        prompt: str,
        conversation_id: str = None,
        parent_id: str = None,
        timeout: int = 360,  # default Ask parameters
        query: str = None,
        numResults: int = 3,
        timePeriod: str = "",
        region: str = "",
        reply_in: str = "undefined",  # Webify parameters
    ) -> tuple[dict, list]:
        """
        Ask a question to the chatbot, but providing search results for query (if not specified, prompt is used)
        Returns message adapted for markdown
        """
        query = query or prompt
        webPrompt, headers = webify(
            text=prompt,
            query=query,
            numResults=numResults,
            timePeriod=timePeriod,
            region=region,
            reply_in=reply_in,
        )
        async for data in self.ask(prompt, conversation_id, parent_id, timeout):
            data["message"] = beatifyMarkdown(data["message"], headers)
            yield data


get_input = V1.logger(is_timed=False)(V1.get_input)


@V1.logger(is_timed=False)
def main(config: dict) -> NoReturn:
    """
    Main function for the chatGPT program.
    """
    print("Logging in...")
    chatbot = WebChatbot(
        config,
        conversation_id=config.get("conversation_id"),
        parent_id=config.get("parent_id"),
    )

    def handle_commands(command: str) -> bool:
        if command == "!help":
            print(
                """
            !help - Show this message
            !reset - Forget the current conversation
            !config - Show the current configuration
            !rollback x - Rollback the conversation (x being the number of messages to rollback)
            !exit - Exit this program
            !setconversation - Changes the conversation
            """,
            )
        elif command == "!reset":
            chatbot.reset_chat()
            print("Chat session successfully reset.")
        elif command == "!config":
            print(json.dumps(chatbot.config, indent=4))
        elif command.startswith("!rollback"):
            try:
                rollback = int(command.split(" ")[1])
            except IndexError:
                logging.exception(
                    "No number specified, rolling back 1 message",
                    stack_info=True,
                )
                rollback = 1
            chatbot.rollback_conversation(rollback)
            print(f"Rolled back {rollback} messages.")
        elif command.startswith("!setconversation"):
            try:
                chatbot.conversation_id = chatbot.config[
                    "conversation_id"
                ] = command.split(" ")[1]
                print("Conversation has been changed")
            except IndexError:
                log.exception(
                    "Please include conversation UUID in command",
                    stack_info=True,
                )
                print("Please include conversation UUID in command")
        elif command == "!exit":
            sys.exit(0)
        else:
            return False
        return True

    session = V1.create_session()
    completer = V1.create_completer(
        ["!help", "!reset", "!config", "!rollback", "!exit", "!setconversation"],
    )
    print()
    try:
        while True:
            print(V1.bcolors.OKBLUE + V1.bcolors.BOLD + "You:" + V1.bcolors.ENDC)

            prompt = get_input(session=session, completer=completer)
            if prompt.startswith("!") and handle_commands(prompt):
                continue

            print()
            print(V1.bcolors.OKGREEN + V1.bcolors.BOLD + "Chatbot: ")
            prev_text = ""
            for data in chatbot.webAsk(prompt):
                message = data["message"][len(prev_text) :]
                print(message, end="", flush=True)
                prev_text = data["message"]
            print(V1.bcolors.ENDC)
            print()
    except (KeyboardInterrupt, EOFError):
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    print(
        """
        WebGPT module. Copies functionality from WebChatGPT browser extension. Made by Nymda (github.com/NymdaFromSalad)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print(
        f"{V1.bcolors.BOLD} {V1.bcolors.WARNING} Press Esc followed by Enter or Alt+Enter to send a message. {V1.bcolors.ENDC}",
    )
    main(V1.configure())

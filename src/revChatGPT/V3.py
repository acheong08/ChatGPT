"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys
from typing import NoReturn

import requests
import tiktoken

from .utils import create_completer
from .utils import create_keybindings
from .utils import create_session
from .utils import get_input


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(
        self,
        api_key: str,
        engine: str = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo",
        proxy: str = None,
        max_tokens: int = 3000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        reply_count: int = 1,
        system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
    ) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        self.engine = engine
        self.session = requests.Session()
        self.api_key = api_key
        self.proxy = proxy

        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.reply_count = reply_count

        if self.proxy:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.session.proxies = proxies
        self.conversation: dict = {
            "default": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
            ],
        }
        if max_tokens > 4000:
            raise Exception("Max tokens cannot be greater than 4000")

        if self.get_token_count("default") > self.max_tokens:
            raise Exception("System prompt is too long")

    def add_to_conversation(
        self,
        message: str,
        role: str,
        convo_id: str = "default",
    ) -> None:
        """
        Add a message to the conversation
        """
        self.conversation[convo_id].append({"role": role, "content": message})

    def __truncate_conversation(self, convo_id: str = "default") -> None:
        """
        Truncate the conversation
        """
        while True:
            if (
                self.get_token_count(convo_id) > self.max_tokens
                and len(self.conversation[convo_id]) > 1
            ):
                # Don't remove the first message
                self.conversation[convo_id].pop(1)
            else:
                break

    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    def get_token_count(self, convo_id: str = "default") -> int:
        """
        Get token count
        """
        if self.engine not in ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]:
            raise NotImplementedError("Unsupported engine {self.engine}")

        encoding = tiktoken.encoding_for_model(self.engine)

        num_tokens = 0
        for message in self.conversation[convo_id]:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens

    def get_max_tokens(self, convo_id: str) -> int:
        """
        Get max tokens
        """
        return self.max_tokens - self.get_token_count(convo_id)

    def ask_stream(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> str:
        """
        Ask a question
        """
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        # Get response
        response = self.session.post(
            os.environ.get("API_URL") or "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {kwargs.get('api_key', self.api_key)}"},
            json={
                "model": self.engine,
                "messages": self.conversation[convo_id],
                "stream": True,
                # kwargs
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "presence_penalty": kwargs.get(
                    "presence_penalty",
                    self.presence_penalty,
                ),
                "frequency_penalty": kwargs.get(
                    "frequency_penalty",
                    self.frequency_penalty,
                ),
                "n": kwargs.get("n", self.reply_count),
                "user": role,
                "max_tokens": self.get_max_tokens(convo_id=convo_id),
            },
            stream=True,
        )
        if response.status_code != 200:
            raise Exception(
                f"Error: {response.status_code} {response.reason} {response.text}",
            )
        response_role: str = None
        full_response: str = ""
        for line in response.iter_lines():
            if not line:
                continue
            # Remove "data: "
            line = line.decode("utf-8")[6:]
            if line == "[DONE]":
                break
            resp: dict = json.loads(line)
            choices = resp.get("choices")
            if not choices:
                continue
            delta = choices[0].get("delta")
            if not delta:
                continue
            if "role" in delta:
                response_role = delta["role"]
            if "content" in delta:
                content = delta["content"]
                full_response += content
                yield content
        self.add_to_conversation(full_response, response_role, convo_id=convo_id)

    def ask(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        **kwargs,
    ) -> str:
        """
        Non-streaming ask
        """
        response = self.ask_stream(
            prompt=prompt,
            role=role,
            convo_id=convo_id,
            **kwargs,
        )
        full_response: str = "".join(response)
        return full_response

    def rollback(self, n: int = 1, convo_id: str = "default") -> None:
        """
        Rollback the conversation
        """
        for _ in range(n):
            self.conversation[convo_id].pop()

    def reset(self, convo_id: str = "default", system_prompt: str = None) -> None:
        """
        Reset the conversation
        """
        self.conversation[convo_id] = [
            {"role": "system", "content": system_prompt or self.system_prompt},
        ]

    def save(self, file: str, *convo_ids: str) -> bool:
        """
        Save the conversation to a JSON file
        """
        try:
            with open(file, "w", encoding="utf-8") as f:
                if convo_ids:
                    json.dump({k: self.conversation[k] for k in convo_ids}, f, indent=2)
                else:
                    json.dump(self.conversation, f, indent=2)
        except (FileNotFoundError, KeyError):
            return False
        return True
        # print(f"Error: {file} could not be created")

    def load(self, file: str, *convo_ids: str) -> bool:
        """
        Load the conversation from a JSON  file
        """
        try:
            with open(file, encoding="utf-8") as f:
                if convo_ids:
                    convos = json.load(f)
                    self.conversation.update({k: convos[k] for k in convo_ids})
                else:
                    self.conversation = json.load(f)
        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            return False
        return True

    def load_config(self, file: str, no_api_key: bool = False) -> bool:
        """
        Load the configuration from a JSON file
        """
        try:
            with open(file, encoding="utf-8") as f:
                config = json.load(f)
                if config is not None:
                    self.api_key = config.get("api_key") or self.api_key
                    if self.api_key is None:
                        # Make sure the API key is set
                        raise Exception("Error: API key is not set")
                    self.engine = config.get("engine") or self.engine
                    self.temperature = config.get("temperature") or self.temperature
                    self.top_p = config.get("top_p") or self.top_p
                    self.presence_penalty = (
                        config.get("presence_penalty") or self.presence_penalty
                    )
                    self.frequency_penalty = (
                        config.get("frequency_penalty") or self.frequency_penalty
                    )
                    self.reply_count = config.get("reply_count") or self.reply_count
                    self.max_tokens = config.get("max_tokens") or self.max_tokens

                    if config.get("system_prompt") is not None:
                        self.system_prompt = (
                            config.get("system_prompt") or self.system_prompt
                        )
                        self.reset(system_prompt=self.system_prompt)

                    if config.get("proxy") is not None:
                        self.proxy = config.get("proxy") or self.proxy
                        proxies = {
                            "http": self.proxy,
                            "https": self.proxy,
                        }
                        self.session.proxies = proxies
        except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
            return False
        return True


class ChatbotCLI(Chatbot):
    def print_config(self, convo_id: str = "default") -> None:
        """
        Prints the current configuration
        """
        print(
            f"""
ChatGPT Configuration:
  Conversation ID:  {convo_id}
  Messages:         {len(self.conversation[convo_id])}
  Tokens used:      {( num_tokens := self.get_token_count(convo_id) )} / {self.max_tokens}
  Cost:             {"${:.5f}".format(( num_tokens / 1000 ) * 0.002)}
  Engine:           {self.engine}
  Temperature:      {self.temperature}
  Top_p:            {self.top_p}
  Reply count:      {self.reply_count}
            """,
        )

    def print_help(self) -> None:
        """
        Prints the help message
        """
        print(
            """
Commands:
  !help            Display this message
  !rollback n      Rollback the conversation by n messages
  !save file [ids] Save all or specificied conversation/s to a JSON file
  !load file [ids] Load all or specificied conversation/s from a JSON file
  !reset           Reset the conversation
  !exit            Quit chat

Config Commands:
  !config          Display the current config
  !load_config fileLoad the config from a JSON file
  !temperature n   Set the temperature to n
  !top_p n         Set the top_p to n
  !reply_count n   Set the reply_count to n
  !engine engine   Sets the chat model to engine
  """,
        )

    def handle_commands(self, input: str, convo_id: str = "default") -> bool:
        """
        Handle chatbot commands
        """
        command, *value = input.split(" ")
        if command == "!help":
            self.print_help()
        elif command == "!exit":
            sys.exit()
        elif command == "!reset":
            self.reset(convo_id=convo_id)
            print("\nConversation has been reset")
        elif command == "!config":
            self.print_config(convo_id=convo_id)
        elif command == "!rollback":
            self.rollback(int(value[0]), convo_id=convo_id)
            print(f"\nRolled back by {value[0]} messages")
        elif command == "!save":
            if is_saved := self.save(*value):
                convo_ids = value[1:] or self.conversation.keys()
                print(
                    f"Saved conversation{'s' if len(convo_ids) > 1 else ''} {', '.join(convo_ids)} to {value[0]}",
                )
            else:
                print(f"Error: {value[0]} could not be created")

        elif command == "!load":
            if is_loaded := self.load(*value):
                convo_ids = value[1:] or self.conversation.keys()
                print(
                    f"Loaded conversation{'s' if len(convo_ids) > 1 else ''} {', '.join(convo_ids)} from {value[0]}",
                )
            else:
                print(f"Error: {value[0]} could not be loaded")
        elif command == "!load_config":
            if is_loaded := self.load_config(*value):
                print(f"Loaded config from {value[0]}")
            else:
                print(f"Error: {value[0]} could not be loaded")
        elif command == "!temperature":
            self.temperature = float(value[0])
            print(f"\nTemperature set to {value[0]}")
        elif command == "!top_p":
            self.top_p = float(value[0])
            print(f"\nTop_p set to {value[0]}")
        elif command == "!reply_count":
            self.reply_count = int(value[0])
            print(f"\nReply count set to {value[0]}")
        elif command == "!engine":
            self.engine = value[0]
            print(f"\nEngine set to {value[0]}")
        else:
            return False

        return True


def main() -> NoReturn:
    """
    Main function
    """
    print(
        """
    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT
    """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press Esc followed by Enter or Alt+Enter to send a message.\n")

    # Get API key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="Temperature for response",
    )
    parser.add_argument(
        "--no_stream",
        action="store_true",
        help="Disable streaming",
    )
    parser.add_argument(
        "--base_prompt",
        type=str,
        default="You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
        help="Base prompt for chatbot",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="Proxy address",
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=1,
        help="Top p for response",
    )
    parser.add_argument(
        "--reply_count",
        type=int,
        default=1,
        help="Number of replies for each prompt",
    )
    parser.add_argument(
        "--enable_internet",
        action="store_true",
        help="Allow ChatGPT to search the internet",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config.v3.json",
    )
    parser.add_argument(
        "--submit_key",
        type=str,
        default=None,
        help="""
        Custom submit key for chatbot. For more information on keys, see README
        """,
    )
    args = parser.parse_args()
    # Load config
    if args.config is not None:
        # Initialize chatbot
        chatbot = ChatbotCLI("placeholder")
        no_api_key = args.api_key is None
        chatbot.load_config(args.config, no_api_key=no_api_key)
    else:
        if args.api_key is None:
            print(
                "Add a config.v3.json and add the path using --config or add an api_key using --api_key",
            )
            # raising at top level is messy and can confuse some people
            return

        chatbot = ChatbotCLI(
            api_key=args.api_key,
            system_prompt=args.base_prompt,
            proxy=args.proxy,
            temperature=args.temperature,
            top_p=args.top_p,
            reply_count=args.reply_count,
        )

    # Check if internet is enabled
    if args.enable_internet:
        from importlib.resources import path

        config = path("revChatGPT", "config").__str__()
        chatbot.load(os.path.join(config, "enable_internet.json"))

    session = create_session()
    completer = create_completer(
        [
            "!help",
            "!exit",
            "!reset",
            "!rollback",
            "!config",
            "!engine",
            "!temperture",
            "!top_p",
            "!reply_count",
            "!save",
            "!load",
            "!load_config",
        ],
    )
    key_bindings = create_keybindings()
    if args.submit_key:
        key_bindings = create_keybindings(args.submit_key)
    # Start chat
    while True:
        print()
        try:
            print("User: ")
            prompt = get_input(
                session=session,
                completer=completer,
                key_bindings=key_bindings,
            )
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        if prompt.startswith("!") and chatbot.handle_commands(prompt):
            continue
        print()
        print("ChatGPT: ", flush=True)
        if args.enable_internet:
            query = chatbot.ask(
                f'This is a prompt from a user to a chatbot: "{prompt}". Respond with "none" if it is directed at the chatbot or cannot be answered by an internet search. Otherwise, respond with a possible search query to a search engine. Do not write any additional text. Make it as minimal as possible',
                convo_id="search",
                temperature=0.0,
            ).strip()
            print("Searching for: ", query, "")
            # Get search results
            search_results = '{"results": "No search results"}'
            if query != "none":
                resp = requests.post(
                    url="https://ddg-api.herokuapp.com/search",
                    json={"query": query, "limit": 3},
                    timeout=10,
                )
                resp.encoding = "utf-8" if resp.encoding is None else resp.encoding
                search_results = resp.text
            print(json.dumps(json.loads(search_results), indent=4))
            chatbot.add_to_conversation(
                f"Search results:{search_results}",
                "system",
                convo_id="default",
            )
            if args.no_stream:
                print(chatbot.ask(prompt, "user", convo_id="default"))
            else:
                for query in chatbot.ask_stream(prompt):
                    print(query, end="", flush=True)
        elif args.no_stream:
            print(chatbot.ask(prompt, "user"))
        else:
            for query in chatbot.ask_stream(prompt):
                print(query, end="", flush=True)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

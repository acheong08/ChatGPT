"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys
from importlib.resources import path
from pathlib import Path
from typing import AsyncGenerator
from typing import NoReturn

import httpx
import requests
import tiktoken

from . import __version__
from . import typings as t
from .utils import create_completer
from .utils import create_keybindings
from .utils import create_session
from .utils import get_filtered_keys_from_object
from .utils import get_input

ENGINES = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-4-0613",
    "gpt-4-32k-0613",
]


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(
        self,
        api_key: str,
        engine: str = os.environ.get("GPT_ENGINE") or "gpt-3.5-turbo",
        proxy: str = None,
        timeout: float = None,
        max_tokens: int = None,
        temperature: float = 0.5,
        top_p: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        reply_count: int = 1,
        truncate_limit: int = None,
        system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
    ) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        self.engine: str = engine
        self.api_key: str = api_key
        self.system_prompt: str = system_prompt
        self.max_tokens: int = max_tokens or (
            31000
            if "gpt-4-32k" in engine
            else 7000
            if "gpt-4" in engine
            else 15000
            if "gpt-3.5-turbo-16k" in engine
            else 4000
        )
        self.truncate_limit: int = truncate_limit or (
            30500
            if "gpt-4-32k" in engine
            else 6500
            if "gpt-4" in engine
            else 14500
            if "gpt-3.5-turbo-16k" in engine
            else 3500
        )
        self.temperature: float = temperature
        self.top_p: float = top_p
        self.presence_penalty: float = presence_penalty
        self.frequency_penalty: float = frequency_penalty
        self.reply_count: int = reply_count
        self.timeout: float = timeout
        self.proxy = proxy
        self.session = requests.Session()
        self.session.proxies.update(
            {
                "http": proxy,
                "https": proxy,
            },
        )
        if proxy := (
            proxy or os.environ.get("all_proxy") or os.environ.get("ALL_PROXY") or None
        ):
            if "socks5h" not in proxy:
                self.aclient = httpx.AsyncClient(
                    follow_redirects=True,
                    proxies=proxy,
                    timeout=timeout,
                )
        else:
            self.aclient = httpx.AsyncClient(
                follow_redirects=True,
                proxies=proxy,
                timeout=timeout,
            )

        self.conversation: dict[str, list[dict]] = {
            "default": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
            ],
        }

        if self.get_token_count("default") > self.max_tokens:
            raise t.ActionRefuseError("System prompt is too long")

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
                self.get_token_count(convo_id) > self.truncate_limit
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
        if self.engine not in ENGINES:
            raise NotImplementedError(
                f"Engine {self.engine} is not supported. Select from {ENGINES}",
            )
        tiktoken.model.MODEL_TO_ENCODING["gpt-4"] = "cl100k_base"

        encoding = tiktoken.encoding_for_model(self.engine)

        num_tokens = 0
        for message in self.conversation[convo_id]:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 5
            for key, value in message.items():
                if value:
                    num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += 5  # role is always required and always 1 token
        num_tokens += 5  # every reply is primed with <im_start>assistant
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
        model: str = None,
        pass_history: bool = True,
        **kwargs,
    ):
        """
        Ask a question
        """
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        # Get response
        if os.environ.get("API_URL") and os.environ.get("MODEL_NAME"):
            # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=rest-api
            url = (
                os.environ.get("API_URL")
                + "openai/deployments/"
                + os.environ.get("MODEL_NAME")
                + "/chat/completions?api-version=2023-05-15"
            )
            headers = {"Content-Type": "application/json", "api-key": self.api_key}
        else:
            url = (
                os.environ.get("API_URL")
                or "https://api.openai.com/v1/chat/completions"
            )
            headers = {"Authorization": f"Bearer {kwargs.get('api_key', self.api_key)}"}
        response = self.session.post(
            url,
            headers=headers,
            json={
                "model": os.environ.get("MODEL_NAME") or model or self.engine,
                "messages": self.conversation[convo_id] if pass_history else [prompt],
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
                "max_tokens": min(
                    self.get_max_tokens(convo_id=convo_id),
                    kwargs.get("max_tokens", self.max_tokens),
                ),
            },
            timeout=kwargs.get("timeout", self.timeout),
            stream=True,
        )
        if response.status_code != 200:
            raise t.APIConnectionError(
                f"{response.status_code} {response.reason} {response.text}",
            )
        response_role: str or None = None
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

    async def ask_stream_async(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        model: str = None,
        pass_history: bool = True,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Ask a question
        """
        # Make conversation if it doesn't exist
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
        self.add_to_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        # Get response
        async with self.aclient.stream(
            "post",
            os.environ.get("API_URL") or "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {kwargs.get('api_key', self.api_key)}"},
            json={
                "model": model or self.engine,
                "messages": self.conversation[convo_id] if pass_history else [prompt],
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
                "max_tokens": min(
                    self.get_max_tokens(convo_id=convo_id),
                    kwargs.get("max_tokens", self.max_tokens),
                ),
            },
            timeout=kwargs.get("timeout", self.timeout),
        ) as response:
            if response.status_code != 200:
                await response.aread()
                raise t.APIConnectionError(
                    f"{response.status_code} {response.reason_phrase} {response.text}",
                )

            response_role: str = ""
            full_response: str = ""
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                # Remove "data: "
                line = line[6:]
                if line == "[DONE]":
                    break
                resp: dict = json.loads(line)
                if "error" in resp:
                    raise t.ResponseError(f"{resp['error']}")
                choices = resp.get("choices")
                if not choices:
                    continue
                delta: dict[str, str] = choices[0].get("delta")
                if not delta:
                    continue
                if "role" in delta:
                    response_role = delta["role"]
                if "content" in delta:
                    content: str = delta["content"]
                    full_response += content
                    yield content
        self.add_to_conversation(full_response, response_role, convo_id=convo_id)

    async def ask_async(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        model: str = None,
        pass_history: bool = True,
        **kwargs,
    ) -> str:
        """
        Non-streaming ask
        """
        response = self.ask_stream_async(
            prompt=prompt,
            role=role,
            convo_id=convo_id,
            **kwargs,
        )
        full_response: str = "".join([r async for r in response])
        return full_response

    def ask(
        self,
        prompt: str,
        role: str = "user",
        convo_id: str = "default",
        model: str = None,
        pass_history: bool = True,
        **kwargs,
    ) -> str:
        """
        Non-streaming ask
        """
        response = self.ask_stream(
            prompt=prompt,
            role=role,
            convo_id=convo_id,
            model=model,
            pass_history=pass_history,
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

    def save(self, file: str, *keys: str) -> None:
        """
        Save the Chatbot configuration to a JSON file
        """
        with open(file, "w", encoding="utf-8") as f:
            data = {
                key: self.__dict__[key]
                for key in get_filtered_keys_from_object(self, *keys)
            }
            # saves session.proxies dict as session
            # leave this here for compatibility
            data["session"] = data["proxy"]
            del data["aclient"]
            json.dump(
                data,
                f,
                indent=2,
            )

    def load(self, file: Path, *keys_: str) -> None:
        """
        Load the Chatbot configuration from a JSON file
        """
        with open(file, encoding="utf-8") as f:
            # load json, if session is in keys, load proxies
            loaded_config = json.load(f)
            keys = get_filtered_keys_from_object(self, *keys_)

            if (
                "session" in keys
                and loaded_config["session"]
                or "proxy" in keys
                and loaded_config["proxy"]
            ):
                self.proxy = loaded_config.get("session", loaded_config["proxy"])
                self.session = httpx.Client(
                    follow_redirects=True,
                    proxies=self.proxy,
                    timeout=self.timeout,
                    cookies=self.session.cookies,
                    headers=self.session.headers,
                )
                self.aclient = httpx.AsyncClient(
                    follow_redirects=True,
                    proxies=self.proxy,
                    timeout=self.timeout,
                    cookies=self.session.cookies,
                    headers=self.session.headers,
                )
            if "session" in keys:
                keys.remove("session")
            if "aclient" in keys:
                keys.remove("aclient")
            self.__dict__.update({key: loaded_config[key] for key in keys})


class ChatbotCLI(Chatbot):
    """
    Command Line Interface for Chatbot
    """

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
  !help             Display this message
  !rollback n       Rollback the conversation by n messages
  !save file [keys] Save the Chatbot configuration to a JSON file
  !load file [keys] Load the Chatbot configuration from a JSON file
  !reset            Reset the conversation
  !exit             Quit chat

Config Commands:
  !config           Display the current config
  !temperature n    Set the temperature to n
  !top_p n          Set the top_p to n
  !reply_count n    Set the reply_count to n
  !engine engine    Sets the chat model to engine

Examples:
  !save c.json               Saves all ChatbotGPT class variables to c.json
  !save c.json engine top_p  Saves only temperature and top_p to c.json
  !load c.json not engine    Loads all but engine from c.json
  !load c.json session       Loads session proxies from c.json


  """,
        )

    def handle_commands(self, prompt: str, convo_id: str = "default") -> bool:
        """
        Handle chatbot commands
        """
        command, *value = prompt.split(" ")
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
            self.save(*value)
            print(
                f"Saved {', '.join(value[1:]) if len(value) > 1 else 'all'} keys to {value[0]}",
            )
        elif command == "!load":
            self.load(*value)
            print(
                f"Loaded {', '.join(value[1:]) if len(value) > 1 else 'all'} keys from {value[0]}",
            )
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
            if len(value) > 0:
                self.engine = value[0]
            print(f"\nEngine set to {self.engine}")
        else:
            return False

        return True


def main() -> NoReturn:
    """
    Main function
    """
    print(
        f"""
    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT
    Version: {__version__}
    """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press Esc followed by Enter or Alt+Enter to send a message.\n")

    # Get API key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
        required="--config" not in sys.argv,
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
        default=False,
        help="Path to V3 config json file",
    )
    parser.add_argument(
        "--submit_key",
        type=str,
        default=None,
        help="Custom submit key for chatbot. For more information on keys, see README",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        choices=ENGINES,
    )

    parser.add_argument(
        "--truncate_limit",
        type=int,
        default=None,
    )

    args, _ = parser.parse_known_args()

    # Initialize chatbot
    if config := args.config or os.environ.get("GPT_CONFIG_PATH"):
        chatbot = ChatbotCLI(args.api_key)
        try:
            chatbot.load(config)
        except Exception as err:
            print(f"Error: {args.config} could not be loaded")
            raise err
    else:
        chatbot = ChatbotCLI(
            api_key=args.api_key,
            system_prompt=args.base_prompt,
            proxy=args.proxy,
            temperature=args.temperature,
            top_p=args.top_p,
            reply_count=args.reply_count,
            engine=args.model,
            truncate_limit=args.truncate_limit,
        )
    # Check if internet is enabled
    if args.enable_internet:
        config = path("revChatGPT", "config").__str__()
        chatbot.load(Path(config, "enable_internet.json"), "conversation")

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
        if prompt.startswith("!"):
            try:
                chatbot.handle_commands(prompt)
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as err:
                print(f"Error: {err}")
                continue
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
    except Exception as exc:
        raise t.CLIError("Command line program unknown error") from exc
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

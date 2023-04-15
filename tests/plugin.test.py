import datetime
import json
from typing import Optional

import requests
import revChatGPT.V1
from revChatGPT.V1 import Chatbot
from revChatGPT.V1 import uuid

config = revChatGPT.V1.configure()
cbt = Chatbot(config)


def construct_message(
    msg: str,
    role: str,
    name: Optional[str] = None,
    content_type: str = "text",
) -> str:
    return {
        "id": str(uuid.uuid4()),
        "author": {
            "role": role,
            "name": name,
        },
        "content": {"content_type": content_type, "parts": [msg]},
    }


def search(q: str, region: str = "wt-wt", time: int = None) -> str:
    url = f"https://ddg-webapp-aagd.vercel.app/search?q={q}&region={region}" + (
        f"&t={time}" if time else ""
    )
    r = requests.get(url)
    return json.dumps(r.json(), ensure_ascii=False)


def browse(url: str) -> str:
    r = requests.get(url)
    return r.text


if __name__ == "__main__":
    promt = f"""Knowledge cutoff: 2021-09
Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

###Available Tools:
DDG-Searcher

You have the tool DDG-Searcher and it works in the following manner:

You need to call api to perform the tool and you do not to run python.
DDG-Searcher Function:
  1. search
    - Description: Searches DuckDuckGo for the given query and returns a list of search results. It supports multiple languages.
    - Parameters:
      - q: string (required) - the search query.
      - region: string (optional) - the region to search in, default is 'wt-wt'.
      - time: string (optional) - the time filter, possible values are 'd', 'w', 'm', 'y', and None (default).
    - Returns: A JSON array of search results, each result contains:
      - title: string - the title of the search result.
      - href: string - the URL of the search result.
      - body: string - the partial content of the search result.
  2. browse
    - Description: Retrieves the content of a website using its URL.
    - Parameters:
      - url: string (required) - the URL of the website to browse.
    - Returns: A string containing the content of the website."""
    result = {}

    for i in cbt.ask(promt, model=""):
        result = i
    print(result)
    for i in cbt.ask("帮我查查怎么喝水。"):  # test
        result = i
    while not result["end_turn"]:
        print(result)
        recipient = result["recipient"]
        if recipient == "DDG-Searcher":
            if result["message"][:6] in ["search", "browse"]:
                try:
                    msg = construct_message(
                        eval(result["message"]),
                        "tool",
                        "DDG-Searcher",
                    )
                except Exception as e:
                    msg = construct_message(str(e), "tool", "DDG-Searcher")
            else:
                msg = construct_message(
                    "Error: don't find the command",
                    "tool",
                    "DDG-Searcher",
                )
        elif recipient == "python":
            msg = construct_message(
                "Error: python isn't supported.",
                "tool",
                "DDG-Searcher",
            )
        else:
            msg = construct_message(
                "Error: don't find the recipient",
                "tool",
                "DDG-Searcher",
            )
        for i in cbt.post_messages([msg]):
            result = i
    print(result)

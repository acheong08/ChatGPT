"""
A simple wrapper for the official ChatGPT API
"""
import argparse
import json
import os
import sys

import tiktoken
from .V3 import Chatbot as ChatbotV3
from .V3 import main




class Chatbot(ChatbotV3):
    def __init__(self, api_key: str,
                 engine: str = os.environ.get("GPT_ENGINE") or "gpt-4",
                 proxy: str = None,
                 max_tokens: int = 3000,
                 temperature: float = 0.5,
                 top_p: float = 1.0,
                 presence_penalty: float = 0.0,
                 frequency_penalty: float = 0.0,
                 reply_count: int = 1,
                 system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally", ):

        ChatbotV3.__init__(self, api_key, engine, proxy, max_tokens, temperature, top_p, presence_penalty,
                           frequency_penalty, reply_count, system_prompt)



    def get_token_count(self, convo_id: str = "default") -> int:
        """
        Get token count
        """
        if self.engine not in ["gpt-4","gpt-4-0314","gpt-4-32k","gpt-4-32k-0314"]:
            raise NotImplementedError("Unsupported engine {self.engine}")

        tiktoken.model.MODEL_PREFIX_TO_ENCODING['gpt-4-'] = 'cl100k_base'
        tiktoken.model.MODEL_TO_ENCODING['gpt-4'] = 'cl100k_base'


        encoding = tiktoken.encoding_for_model(self.engine)

        num_tokens = 0
        for message in self.conversation[convo_id]:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += 1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

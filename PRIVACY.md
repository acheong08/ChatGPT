# Versions 0, 2, and 3

By using these versions, you agree to [OpenAI's privacy policy](https://openai.com/policies/privacy-policy). This repository does not collect any data.

# Version 1

Version 1 requires a cloudflare bypass to access `chat.openai.com`. Therefore, in combination to [OpenAI's privacy policy](https://openai.com/policies/privacy-policy), you must also accept the privacy policy of other providers involved in the process.

- [Microsoft Azure](https://azure.microsoft.com/en-us/support/legal/) - The bypass server is hosted there
- [Cloudflare](https://www.cloudflare.com/privacypolicy/) - Used to prevent abuse
- My own privacy policy

# My privacy policy

My bypass server does not contain any code to log and store data.

# Analytics

This is disabled by default. Set `collect_analytics` to `true` to enable it on V1.

## What will be collected

- Conversation ID -- Train for longer conversations
- Hashed access token (MD5) -- Used to identify and filter out abuse
- Prompt and response -- Used for training the model

## Why?

- To train an open source model based on LLaMA

## Who will have access to the data?

- The prompt and response will be publicly available on GitHub along with the hashed conversation ID.

## How long will the data be stored?

- Once published on GitHub, the data will be stored indefinitely.

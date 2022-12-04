# ChatGPT
Reverse Engineered ChatGPT by OpenAI. Extensible for chatbots etc.

Note: This is a proof of concept. The goal here is to be able to write bots using the API.

# Features
- Scientific knowledge
- Has memory. It remembers the chat history and context
- Uncensored
- No moderation

# Setup
## Get your Bearer token
Go to https://chat.openai.com/chat and log in or sign up
1. Open console with `F12`
2. Go to Network tab in console
3. Find session request (Might need refresh)
4. Copy accessToken value to config.json.example as Authorization
5. Save as config.json
![image](https://user-images.githubusercontent.com/36258159/205446680-b3f40499-9757-428b-9e2f-23e89ca99461.png)
![image](https://user-images.githubusercontent.com/36258159/205446730-793f8187-316c-4ae8-962c-0f4c1ee00bd1.png)

# Running
`python3 ChatGPT.py`

# Known issues
- Access token expires in one hour

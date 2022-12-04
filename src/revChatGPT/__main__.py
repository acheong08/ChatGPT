from revChatGPT import Chatbot
if __name__ == "__main__":
    print("""
    ChatGPT - A simple chatbot using OpenAI's GPT-3 API
    By: github.com/acheong08
    """)
    print("Type '!exit' to exit")
    with open("config.json", "r") as f:
            config = json.load(f)
    chatbot = Chatbot(config)
    while True:
        prompt = input("You: ")
        if prompt == "!exit":
            break
        try:
            response = chatbot.get_chat_response(prompt)
        except Exception as e:
            print("Something went wrong!")
            print(e)
            continue
        print("\n")
        print("Chatbot:", response['message'])
        print("\n")

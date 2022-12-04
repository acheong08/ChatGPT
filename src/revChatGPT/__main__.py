from revChatGPT.revChatGPT import Chatbot
import json

def get_input(prompt):
  # prompt for input
  lines = []
  print(prompt,end="")
  while True:
      line = input()
      if line == "":
          break
      lines.append(line)

  # Join the lines, separated by newlines, and print the result
  user_input = "\n".join(lines)
  #print(user_input)
  return user_input

if __name__ == "__main__":
    print("""
    ChatGPT - A simple chatbot using OpenAI's GPT-3 API
    By: github.com/acheong08
    """)
    print("Type '!exit' to exit")
    print("Press enter twice to submit your question.\n")
    with open("config.json", "r") as f:
            config = json.load(f)
    chatbot = Chatbot(config)
    while True:
        prompt = get_input("You: ")
        if prompt == "!exit":
            break
        try:
            print("Please wait for ChatGPT to formulate its full response...")
            response = chatbot.get_chat_response(prompt)
        except Exception as e:
            print("Something went wrong!")
            print(e)
            continue
        print("\n")
        print("Chatbot:", response['message'])
        print("\n")

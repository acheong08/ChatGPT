import requests
import json
import uuid

class Chatbot:
    config: json
    conversation_id: str
    parent_id: str
    def __init__(self, config, conversation_id=None):
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = self.generate_uuid()

    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return uid
        
    def get_chat_response(self, prompt):
        Authorization = self.config["Authorization"]
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + Authorization,
            "Content-Type": "application/json"
        }
        data = {
            "action":"next",
            "messages":[
                {"id":str(self.generate_uuid()),
                "role":"user",
                "content":{"content_type":"text","parts":[prompt]}
            }],
            "conversation_id":self.conversation_id,
            "parent_message_id":self.parent_id,
            "model":"text-davinci-002-render"
        }
        response = requests.post("https://chat.openai.com/backend-api/conversation", headers=headers, data=json.dumps(data))
        try:
            response = response.text.splitlines()[-4]
        except:
            print(response.text)
            return ValueError("Error: Response is not a text/event-stream")
        try:
            response = response[6:]
        except:
            print(response.text)
            return ValueError("Response is not in the correct format")
        response = json.loads(response)
        self.parent_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        message = response["message"]["content"]["parts"][0]
        return {'message':message, 'conversation_id':self.conversation_id, 'parent_id':self.parent_id}

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
    ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
    Repo: github.com/scottleibrand/ChatGPT
    Forked from: github.com/acheong08/ChatGPT
    """)
    print("Type '!exit' to exit")
    print("Press enter twice to submit your question.")
    with open("config.json", "r") as f:
            config = json.load(f)
    chatbot = Chatbot(config)
    import subprocess
    from subprocess import Popen
    import sys

    while True:
        prompt = get_input("You: ")
        if prompt == "!exit":
            break
        print("Please wait for ChatGPT to formulate its full response...")
        try:
            response = chatbot.get_chat_response(prompt)
        except Exception as e:
            print("Something went wrong!")
            print(e)
            continue
        # Erase the previous line
        sys.stdout.write("\033[F\033[K")

        #print("\n")
        print("Chatbot:", response['message'])
        print("\n")

        arguments=list(sys.argv)
        del arguments[0]

        if len(arguments)>1:
            try:
                process.terminate()
            except NameError:
                print("")
            if len(arguments)>2:

                # Use `python3 ./revChatGPT.py say -v Samantha -r 600`` to make a Mac speak the output
                # using the Samantha voice at 600 words per minute (about 3x)
                arguments.append('"' + response['message'] + '"')
                process = Popen(arguments)
            else:
                process = Popen([arguments[1],"-r 400",response['message']])

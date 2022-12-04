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

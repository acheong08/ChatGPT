from fastapi import FastAPI
from pydantic import BaseModel
from revChatGPT.revChatGPT import Chatbot
import json

class Req(BaseModel):
  prompt: str

with open("config.json", "r") as f:
        config = json.load(f)
chatbot = Chatbot(config)
if 'session_token' in config:
    chatbot.refresh_session()

app = FastAPI()

@app.get("/refresh")
async def refresh():
  return config

@app.post("/ask")
async def ask(req: Req):
  return chatbot.get_chat_response(req.prompt)
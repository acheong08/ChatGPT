import uuid
import socketio
import datetime
import asyncio
import json
import base64
import threading
import time
import sys
import argparse


class ChatGPT:
    def __init__(self, session_token, bypass_node="https://gpt.pawan.krd"):
        self.ready = False
        self.socket = socketio.Client()
        self.socket.connect(bypass_node, transports=['websocket', 'polling'])
        self.session_token = session_token
        self.conversations = []
        self.auth = None
        self.expires = datetime.datetime.now()
        self.token_next_check = datetime.datetime.now()
        self.stop_check_tokens = False
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        # Start a new thread to run check_tokens every 2 minutes
        self.check_tokens_thread = threading.Thread(
            target=self.check_tokens_periodically)
        self.check_tokens_thread.start()

    def on_connect(self):
        print('Connected to server')

    def on_disconnect(self):
        print('Disconnected from server')

    def check_tokens_periodically(self):
        while True:
            if self.stop_check_tokens:
                return
            # Check if token next check time has passed
            if self.token_next_check > datetime.datetime.now():
                time.sleep(1)
                continue
            now = datetime.datetime.now()
            # Use timedelta to subtract time
            offset = datetime.timedelta(milliseconds=2 * 60 * 1000)
            if self.expires < (now - offset) or self.auth is None:
                # Run get_tokens as an asyncio task using run_in_executor
                self.get_tokens()
            # Set the next check time to 2 minutes from now
            self.token_next_check = now + offset
            time.sleep(5)

    def add_conversation(self, id):
        conversation = {
            'id': id,
            'conversation_id': None,
            'parent_id': str(uuid.uuid4()),
            'last_active': datetime.datetime.now()
        }
        self.conversations.append(conversation)
        return conversation

    def get_conversation_by_id(self, id):
        conversation = next(
            (c for c in self.conversations if c['id'] == id), None)
        if conversation is None:
            conversation = self.add_conversation(id)
        else:
            conversation['last_active'] = datetime.datetime.now()
        return conversation

    def wait(self, time):
        return asyncio.sleep(time)

    async def wait_for_ready(self):
        while not self.ready:
            await self.wait(5)
        print("Ready!!")

    async def ask(self, prompt, id="default"):
        if self.auth is None or not self.validate_token(self.auth):
            await self.get_tokens()
        conversation = self.get_conversation_by_id(id)

        # Create a queue to store the data from the callback function
        data_queue = asyncio.Queue()

        # Declare a callback function to process the response
        def ask_callback(data):
            if 'error' in data:
                print(f'Error: {data["error"]}')
            conversation['parent_id'] = data['messageId']
            conversation['conversation_id'] = data['conversationId']
            # Put the data in the queue
            data_queue.put_nowait(data)

        # Use the callback function to process the response
        self.socket.emit('askQuestion', {
            'prompt': prompt,
            'parentId': conversation['parent_id'],
            'conversationId': conversation['conversation_id'],
            'auth': self.auth
        }, callback=ask_callback)

        # Keep checking the queue for data
        while data_queue.empty():
            await self.wait(1)

        # Get the data from the queue
        data = data_queue.get_nowait()
        return data

    def validate_token(self, token):
        if token is None:
            return False
        parsed = json.loads(base64.b64decode(token.split('.')[1]).decode())
        return datetime.datetime.now().timestamp() <= parsed['exp']

    def get_tokens(self):
        time.sleep(1)  # equivalent to await self.wait(1000)
        self.socket.emit('getSession', self.session_token,
                         callback=self.get_tokens_callback)

    def get_tokens_callback(self, data):
        if 'error' in data:
            print(f'Error: {data["error"]}')
            return
        self.session_token = data['sessionToken']
        self.auth = data['auth']
        # Convert 2023-01-31T15:16:58.065Z to datetime object
        self.expires = datetime.datetime.strptime(
            data['expires'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.ready = True

    def close(self):
        self.socket.disconnect()
        self.stop_check_tokens = True
        self.check_tokens_thread.join()
        print("Closed")


def sync_main(args):
    chat = ChatGPT(args.session_token, args.bypass_node)
    # Create loop
    loop = asyncio.new_event_loop()
    # Set
    asyncio.set_event_loop(loop)
    # Run
    loop.run_until_complete(chat.wait_for_ready())
    while True:
        try:
            prompt = input("You: ")
            if prompt == "!exit":
                break
            response = loop.run_until_complete(chat.ask(prompt))
            print(f"\nBot: {response['answer']}\n")
        except KeyboardInterrupt:
            break
    # Close sockets
    chat.close()
    # stop asyncio event loop
    loop.stop()
    # exit
    sys.exit(0)


async def async_main(args):
    if args.session_token is None:
        print("Please provide a session token")
        sys.exit(1)

    chat = ChatGPT(args.session_token, args.bypass_node)
    await asyncio.gather(chat.wait_for_ready())

    while True:
        try:
            prompt = input("You: ")
            if prompt == "!exit":
                break
            response = await chat.ask(prompt)
            print(f"\nBot: {response['answer']}\n")
        except KeyboardInterrupt:
            break
    # Close sockets
    chat.close()
    # exit
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session_token', type=str, default=None)
    parser.add_argument('--bypass_node', type=str,
                        default="https://gpt.pawan.krd")
    parser.add_argument('--async_mode', type=bool, default=False)
    args = parser.parse_args()

    if args.session_token is None:
        print("Please provide a session token")
        sys.exit(1)

    if args.async_mode:
        asyncio.run(async_main(args))
    else:
        sync_main(args)

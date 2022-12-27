import uuid
import re
import json
import tls_client
import undetected_chromedriver as uc
from time import sleep

BASE_URL = "https://chat.openai.com/"


class Chatbot:
    def __init__(self, config, conversation_id=None, parent_id=None) -> None:
        self.config = config
        self.session = tls_client.Session(
            client_identifier="chrome_105"
        )
        self.session.cookies.set(
            "__Secure-next-auth.session-token", config["session_token"])
        if "proxy" in config:
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            self.session.proxies.update(proxies)
        self.refresh_session()
        self.conversation_id = conversation_id
        self.parent_id = parent_id

    def ask(self, prompt, conversation_id=None, parent_id=None):
        self.refresh_session()
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id or self.conversation_id,
            "parent_message_id": parent_id or self.parent_id or str(uuid.uuid4()),
            "model": "text-davinci-002-render",
        }
        response = self.session.post(
            url=BASE_URL + "backend-api/conversation",
            data=json.dumps(data)
        )
        if response.status_code != 200:
            print(response.text)
            self.refresh_session()
            raise Exception("Wrong response code! Refreshing session...")
        else:
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except Exception as exc:
                print("Incorrect response from OpenAI API")
                raise Exception("Incorrect response from OpenAI API") from exc
            # Check if it is JSON
            if response.startswith("{"):
                response = json.loads(response)
                self.parent_id = response["message"]["id"]
                self.conversation_id = response["conversation_id"]
                message = response["message"]["content"]["parts"][0]
                return {
                    "message": message,
                    "conversation_id": self.conversation_id,
                    "parent_id": self.parent_id,
                }
            else:
                return None

    def refresh_session(self):
        url = BASE_URL + "api/auth/session"
        response = self.session.get(url)
        if response.status_code == 403:
            self.get_cf_cookies()
            self.refresh_headers()
            self.refresh_session()
            return
        try:
            if "error" in response.json():
                raise Exception(
                    "Failed to refresh session! Error: " + response.json()["error"])
            elif response.status_code != 200 or response.json() == {} or "accessToken" not in response.json():
                raise Exception("Failed to refresh session!")
            else:
                self.session.headers.update({
                    "Authorization": "Bearer " + response.json()["accessToken"]
                })
        except Exception as exc:
            print("Failed to refresh session!")
            raise Exception("Failed to refresh session!") from exc

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    def get_cf_cookies(self) -> None:
        """
        Get cloudflare cookies.

        :return: None
        """
        self.cookie_found = False
        self.agent_found = False

        def detect_cookies(message):
            if 'params' in message:
                if 'headers' in message['params']:
                    if 'set-cookie' in message['params']['headers']:
                        # Use regex to get the cookie for cf_clearance=*;
                        cookie = re.search(
                            "cf_clearance=.*?;", message['params']['headers']['set-cookie'])
                        if cookie:
                            print(
                                "Found cookie: " + cookie.group(0))
                            # remove the semicolon and 'cf_clearance=' from the string
                            raw_cookie = cookie.group(0)
                            self.config['cf_clearance'] = raw_cookie[13:-1]
                            self.cookie_found = True

        def detect_user_agent(message):
            if 'params' in message:
                if 'headers' in message['params']:
                    if 'user-agent' in message['params']['headers']:
                        # Use regex to get the cookie for cf_clearance=*;
                        user_agent = message['params']['headers']['user-agent']
                        self.config['user_agent'] = user_agent
                        self.agent_found = True
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        print("Spawning browser...")
        driver = uc.Chrome(enable_cdp_events=True, options=options)
        print("Browser spawned.")
        driver.add_cdp_listener(
            "Network.responseReceivedExtraInfo", lambda msg: detect_cookies(msg))
        driver.add_cdp_listener(
            "Network.requestWillBeSentExtraInfo", lambda msg: detect_user_agent(msg))
        driver.get("https://chat.openai.com/chat")
        while not self.agent_found or not self.cookie_found:
            print("Waiting for cookies...")
            sleep(5)
        driver.close()
        driver.quit()
        del driver

    def refresh_headers(self):
        self.session.cookies.set("cf_clearance", self.config["cf_clearance"])
        self.session.headers.update({
            "Accept": "text/event-stream",
            "Authorization": "Bearer ",
            "Content-Type": "application/json",
            "User-Agent": self.config["user_agent"],
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
        })

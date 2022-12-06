# Author: @acheong08@fosstodon.org
# License: MIT
# Description: A Python wrapper for OpenAI's chatbot API
import json
import uuid
import re
import urllib
import tls_client
import requests
from bs4 import BeautifulSoup


class Chatbot:
    config: json
    conversation_id: str
    parent_id: str
    headers: dict
    conversation_id_prev: str
    parent_id_prev: str

    def __init__(self, config, conversation_id=None):
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = self.generate_uuid()
        if 'session_token' in config or ('email' in config and 'password' in config):
            self.refresh_session()

    # Resets the conversation ID and parent ID
    def reset_chat(self):
        self.conversation_id = None
        self.parent_id = self.generate_uuid()

    # Refreshes the headers -- Internal use only
    def refresh_headers(self):
        if 'Authorization' not in self.config:
            self.config['Authorization'] = ''
        elif self.config['Authorization'] == None:
            self.config['Authorization'] = ''
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.config['Authorization'],
            "Content-Type": "application/json",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        }

    # Generates a UUID -- Internal use only
    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return uid

    # Generator for chat stream -- Internal use only
    def get_chat_stream(self, data):
        response = requests.post("https://chat.openai.com/backend-api/conversation",
                                 headers=self.headers, data=json.dumps(data), stream=True, timeout=20)
        for line in response.iter_lines():
            try:
                line = line.decode('utf-8')
                if line == "":
                    continue
                line = line[6:]
                line = json.loads(line)
                try:
                    message = line["message"]["content"]["parts"][0]
                    self.conversation_id = line["conversation_id"]
                    self.parent_id = line["message"]["id"]
                except:
                    continue
                yield {'message': message, 'conversation_id': self.conversation_id, 'parent_id': self.parent_id}
            except:
                continue

    # Gets the chat response as text -- Internal use only
    def get_chat_text(self, data):
        # Create request session
        s = requests.Session()
        # set headers
        s.headers = self.headers
        # Set proxies
        if self.config.get("proxy", "") != "":
            s.proxies = {
                "http": self.config["proxy"],
                "https": self.config["proxy"]
            }
        response = s.post(
            "https://chat.openai.com/backend-api/conversation", data=json.dumps(data))
        try:
            response = response.text.splitlines()[-4]
            response = response[6:]
        except Exception as exc:
            try:
                soup = BeautifulSoup(response.text, 'lxml')
                error_desp = soup.title.text + \
                    soup.find("div", {"id": "message"}).text
            except:
                error_desp = json.loads(response.text)["detail"]
                if "message" in error_desp:
                    error_desp = error_desp["message"]
                raise ValueError(
                    "Response is not in the correct format", error_desp) from exc
        response = json.loads(response)
        self.parent_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        message = response["message"]["content"]["parts"][0]
        return {'message': message, 'conversation_id': self.conversation_id, 'parent_id': self.parent_id}

    # Gets the chat response
    def get_chat_response(self, prompt, output="text"):
        data = {
            "action": "next",
            "messages": [
                {"id": str(self.generate_uuid()),
                 "role": "user",
                 "content": {"content_type": "text", "parts": [prompt]}
                 }],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_id,
            "model": "text-davinci-002-render"
        }
        self.conversation_id_prev = self.conversation_id
        self.parent_id_prev = self.parent_id
        if output == "text":
            return self.get_chat_text(data)
        elif output == "stream":
            return self.get_chat_stream(data)
        else:
            raise ValueError("Output must be either 'text' or 'response'")

    def rollback_conversation(self):
        self.conversation_id = self.conversation_id_prev
        self.parent_id = self.parent_id_prev

    def refresh_session(self):
        if 'session_token' not in self.config and ('email' not in self.config or 'password' not in self.config):
            raise ValueError("No tokens provided")
        elif 'session_token' in self.config:
            if self.config['session_token'] == None or self.config['session_token'] == "":
                raise ValueError("No tokens provided")
            s = requests.Session()
            if self.config.get("proxy", "") != "":
                s.proxies = {
                    "http": self.config["proxy"],
                    "https": self.config["proxy"]
                }
            # Set cookies
            s.cookies.set("__Secure-next-auth.session-token",
                          self.config['session_token'])
            # s.cookies.set("__Secure-next-auth.csrf-token", self.config['csrf_token'])
            response = s.get("https://chat.openai.com/api/auth/session", headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
            })
            try:
                self.config['session_token'] = response.cookies.get(
                    "__Secure-next-auth.session-token")
                self.config['Authorization'] = response.json()["accessToken"]
                self.refresh_headers()
            except Exception as exc:
                print("Error refreshing session")
                print(response.text)
                raise Exception("Error refreshing session") from exc
        elif 'email' in self.config and 'password' in self.config:
            try:
                self.login(self.config['email'], self.config['password'])
            except Exception as exc:
                print("Error refreshing session: ")
                print(exc)
                return exc
        else:
            raise ValueError("No tokens provided")

    def login(self, email, password):
        print("Logging in...")
        use_proxy = False
        proxy = None
        if 'proxy' in self.config:
            if self.config['proxy'] != "":
                use_proxy = True
                proxy = self.config['proxy']
        auth = OpenAIAuth(email, password, use_proxy, proxy)
        try:
            auth.begin()
        except Exception as exc:
            # if ValueError with e as "Captcha detected" fail
            if exc == "Captcha detected":
                print("Captcha not supported. Use session tokens instead.")
                raise ValueError("Captcha detected") from exc
            else:
                raise Exception("Error logging in") from exc
        if auth.access_token != None:
            self.config['Authorization'] = auth.access_token
            if auth.session_token != None:
                self.config['session_token'] = auth.session_token
            else:
                possible_tokens = auth.session.cookies.get(
                    "__Secure-next-auth.session-token")
                if possible_tokens != None:
                    if len(possible_tokens) > 1:
                        self.config['session_token'] = possible_tokens[0]
                    else:
                        try:
                            self.config['session_token'] = possible_tokens
                        except Exception as exc:
                            raise Exception("Error logging in") from exc
            self.refresh_headers()
        else:
            raise Exception("Error logging in")

# Credits to github.com/rawandahmad698/PyChatGPT


class OpenAIAuth:
    def __init__(self, email_address: str, password: str, use_proxy: bool = False, proxy: str = None):
        self.email_address = email_address
        self.password = password
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.session = tls_client.Session(
            client_identifier="chrome_105"
        )
        self.access_token: str = None

    @staticmethod
    def url_encode(string: str) -> str:
        """
        URL encode a string
        :param string:
        :return:
        """
        return urllib.parse.quote(string)

    def begin(self):
        """
            Begin the auth process
        """
        if not self.email_address or not self.password:
            return
        else:

            if self.use_proxy:
                if not self.proxy:
                    return

                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }
                self.session.proxies = proxies

        # First, make a request to https://chat.openai.com/auth/login
        url = "https://chat.openai.com/auth/login"
        headers = {
            "Host": "ask.openai.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            self.part_two()
        else:
            raise Exception("Error logging in")

    def part_two(self):
        """
        In part two, We make a request to https://chat.openai.com/api/auth/csrf and grab a fresh csrf token
        """

        url = "https://chat.openai.com/api/auth/csrf"
        headers = {
            "Host": "ask.openai.com",
            "Accept": "*/*",
            "Connection": "keep-alive",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Referer": "https://chat.openai.com/auth/login",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200 and 'json' in response.headers['Content-Type']:
            csrf_token = response.json()["csrfToken"]
            self.part_three(token=csrf_token)
        else:
            raise Exception("Error logging in")

    def part_three(self, token: str):
        """
        We reuse the token from part to make a request to /api/auth/signin/auth0?prompt=login
        """
        url = "https://chat.openai.com/api/auth/signin/auth0?prompt=login"

        payload = f'callbackUrl=%2F&csrfToken={token}&json=true'
        headers = {
            'Host': 'ask.openai.com',
            'Origin': 'https://chat.openai.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': 'https://chat.openai.com/auth/login',
            'Content-Length': '100',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.session.post(url=url, headers=headers, data=payload)
        if response.status_code == 200 and 'json' in response.headers['Content-Type']:
            url = response.json()["url"]
            self.part_four(url=url)
        elif response.status_code == 400:
            raise Exception("Invalid credentials")
        else:
            raise Exception("Unknown error")

    def part_four(self, url: str):
        """
        We make a GET request to url
        :param url:
        :return:
        """
        headers = {
            'Host': 'auth0.openai.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://chat.openai.com/',
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 302:
            state = re.findall(r"state=(.*)", response.text)[0]
            state = state.split('"')[0]
            self.part_five(state=state)
        else:
            raise Exception("Unknown error")

    def part_five(self, state: str):
        """
        We use the state to get the login page & check for a captcha
        """
        url = f"https://auth0.openai.com/u/login/identifier?state={state}"

        headers = {
            'Host': 'auth0.openai.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://chat.openai.com/',
        }
        response = self.session.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            if soup.find('img', alt='captcha'):
                print("Captcha detected")
                raise ValueError("Captcha detected")
            else:
                self.part_six(state=state, captcha=None)
        else:
            raise ValueError("Invalid response code")

    def part_six(self, state: str, captcha: str or None):
        """
        We make a POST request to the login page with the captcha, email
        :param state:
        :param captcha:
        :return:
        """
        url = f"https://auth0.openai.com/u/login/identifier?state={state}"
        email_url_encoded = self.url_encode(self.email_address)
        payload = f'state={state}&username={email_url_encoded}&captcha={captcha}&js-available=true&webauthn-available=true&is-brave=false&webauthn-platform-available=true&action=default'

        if captcha is None:
            payload = f'state={state}&username={email_url_encoded}&js-available=false&webauthn-available=true&is-brave=false&webauthn-platform-available=true&action=default'

        headers = {
            'Host': 'auth0.openai.com',
            'Origin': 'https://auth0.openai.com',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': f'https://auth0.openai.com/u/login/identifier?state={state}',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.session.post(url, headers=headers, data=payload)
        if response.status_code == 302:
            self.part_seven(state=state)
        else:
            raise Exception("Unknown error")

    def part_seven(self, state: str):
        """
        We enter the password
        :param state:
        :return:
        """
        url = f"https://auth0.openai.com/u/login/password?state={state}"

        email_url_encoded = self.url_encode(self.email_address)
        password_url_encoded = self.url_encode(self.password)
        payload = f'state={state}&username={email_url_encoded}&password={password_url_encoded}&action=default'
        headers = {
            'Host': 'auth0.openai.com',
            'Origin': 'https://auth0.openai.com',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Referer': f'https://auth0.openai.com/u/login/password?state={state}',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.session.post(url, headers=headers, data=payload)
        is_302 = response.status_code == 302
        if is_302:
            new_state = re.findall(r"state=(.*)", response.text)[0]
            new_state = new_state.split('"')[0]
            self.part_eight(old_state=state, new_state=new_state)
        else:
            raise Exception("Unknown error")

    def part_eight(self, old_state: str, new_state):
        url = f"https://auth0.openai.com/authorize/resume?state={new_state}"
        headers = {
            'Host': 'auth0.openai.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Referer': f'https://auth0.openai.com/u/login/password?state={old_state}',
        }
        response = self.session.get(url, headers=headers, allow_redirects=True)
        is_200 = response.status_code == 200
        if is_200:
            soup = BeautifulSoup(response.text, 'lxml')
            # Find __NEXT_DATA__, which contains the data we need, the get accessToken
            next_data = soup.find("script", {"id": "__NEXT_DATA__"})
            # Access Token
            access_token = re.findall(
                r"accessToken\":\"(.*)\"", next_data.text)[0]
            access_token = access_token.split('"')[0]
            # Save access_token and an hour from now on ./Classes/auth.json
            self.save_access_token(access_token=access_token)
        else:
            print("Error logging in")
            raise Exception("Failed to find accessToken")

    def save_access_token(self, access_token: str):
        """
        Save access_token and an hour from now on ./Classes/auth.json
        :param access_token:
        :return:
        """
        if self.part_nine():
            self.access_token = access_token
        else:
            print("Failed to login")
            raise Exception("Failed to login")

    def part_nine(self):
        url = "https://chat.openai.com/api/auth/session"
        headers = {
            "Host": "ask.openai.com",
            "Connection": "keep-alive",
            "If-None-Match": "\"bwc9mymkdm2\"",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Referer": "https://chat.openai.com/chat",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = self.session.get(url, headers=headers)
        is_200 = response.status_code == 200
        if is_200:
            # Get session token
            self.session_token = response.cookies.get(
                "__Secure-next-auth.session-token")
            return True
        else:
            self.session_token = None
            raise Exception("Failed to get session token")

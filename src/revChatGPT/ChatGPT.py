import uuid
import re
import json
import tls_client
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

BASE_URL = "https://chat.openai.com/"


class Chatbot:
    def __init__(self, config, conversation_id=None, parent_id=None) -> None:
        self.config = config
        self.session = tls_client.Session(
            client_identifier="chrome_105"
        )
        if "proxy" in config:
            if type(config["proxy"]) != str:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            self.session.proxies.update(proxies)
        if "debug" in config:
            if type(config["debug"]) != bool:
                raise Exception("Debug must be a boolean!")
            self.debug = config["debug"]
        else:
            self.debug = False
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        # stdout colors
        self.GREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.ENDCOLOR = '\033[0m'
        if "email" in config and "password" in config:
            if type(config["email"]) != str:
                raise Exception("Email must be a string!")
            if type(config["password"]) != str:
                raise Exception("Password must be a string!")
            self.email = config["email"]
            self.password = config["password"]
            self.isMicrosoftLogin = True
            self.microsoft_login()
        elif "session_token" in config:
            if type(config["session_token"]) != str:
                raise Exception("Session token must be a string!")
            self.session.cookies.set(
                "__Secure-next-auth.session-token", config["session_token"])
            self.get_cf_cookies()
        else:
            raise Exception("Invalid config!")
        self.refresh_session()

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
        self.conversation_id_prev_queue.append(
            data["conversation_id"])  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
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
            sleep(1)
            self.refresh_session()
            return
        try:
            if "error" in response.json():
               raise Exception(f"Failed to refresh session! Error: {response.json()['error']}")
            elif response.status_code != 200 or response.json() == {} or "accessToken" not in response.json():
                raise Exception("Failed to refresh session!")
            else:
                self.session.headers.update({
                    "Authorization": "Bearer " + response.json()["accessToken"]
                })
        except Exception as exc:
            print("Failed to refresh session!")
            if self.isMicrosoftLogin:
                print("Attempting to re-authenticate...")
                self.microsoft_login()
            else: 
                raise Exception("Failed to refresh session!") from exc

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())
    def microsoft_login(self) -> None:
        """
        Login to OpenAI.

        :return: None
        """
        # Open the browser
        self.cf_cookie_found = False
        self.session_cookie_found = False
        self.agent_found = False
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
            "Network.responseReceivedExtraInfo", lambda msg: self.detect_cookies(msg))
        driver.add_cdp_listener(
            "Network.requestWillBeSentExtraInfo", lambda msg: self.detect_user_agent(msg))
        driver.get(BASE_URL)
        while not self.agent_found or not self.cf_cookie_found:
            print("Waiting for cookies...")
            sleep(5)
        self.refresh_headers()
        # Wait for the login button to appear
        WebDriverWait(driver,120).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Log in')]")))
        # Click the login button
        driver.find_element(by=By.XPATH,value="//button[contains(text(), 'Log in')]").click()
        # Wait for the Login with Microsoft button to be clickable
        WebDriverWait(driver,60).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-provider='windowslive']")))
        # Click the Login with Microsoft button
        driver.find_element(by=By.XPATH,value="//button[@data-provider='windowslive']").click()
        # Wait for the email input field to appear
        WebDriverWait(driver,60).until(EC.visibility_of_element_located(
                (By.XPATH, "//input[@type='email']")))
        # Enter the email
        driver.find_element(by=By.XPATH,value="//input[@type='email']").send_keys(self.config["email"])
        # Wait for the Next button to be clickable
        WebDriverWait(driver,60).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='submit']")))
        # Click the Next button
        driver.find_element(by=By.XPATH,value="//input[@type='submit']").click()
        # Wait for the password input field to appear
        WebDriverWait(driver,60).until(EC.visibility_of_element_located(
                (By.XPATH, "//input[@type='password']")))
        # Enter the password
        driver.find_element(by=By.XPATH,value="//input[@type='password']").send_keys(self.config["password"])
        # Wait for the Sign in button to be clickable
        WebDriverWait(driver,60).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='submit']")))
        # Click the Sign in button
        driver.find_element(by=By.XPATH,value="//input[@type='submit']").click()
        # Wait for the Allow button to appear
        WebDriverWait(driver,60).until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@value='Yes']")))                
        # click Yes button
        driver.find_element(by=By.XPATH,value="//input[@value='Yes']").click()
        # wait for input box to appear (to make sure we're signed in)
        WebDriverWait(driver,60).until(EC.visibility_of_element_located(
                (By.XPATH, "//textarea")))
        while not self.session_cookie_found:
            print("Waiting for session cookie...")
            sleep(5)
        print(self.GREEN + "Login successful." + self.ENDCOLOR)
        # Close the browser
        driver.close()
        driver.quit()
        del driver
    def get_cf_cookies(self) -> None:
        """
        Get cloudflare cookies.

        :return: None
        """
        self.cf_cookie_found = False
        self.agent_found = False
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
            "Network.responseReceivedExtraInfo", lambda msg: self.detect_cookies(msg))
        driver.add_cdp_listener(
            "Network.requestWillBeSentExtraInfo", lambda msg: self.detect_user_agent(msg))
        driver.get("https://chat.openai.com/chat")
        while not self.agent_found or not self.cf_cookie_found:
            print("Waiting for cookies...")
            sleep(5)
        driver.close()
        driver.quit()
        del driver
        self.refresh_headers()
    def detect_cookies(self, message):
        if 'params' in message:
            if 'headers' in message['params']:
                if 'set-cookie' in message['params']['headers']:
                    # Use regex to get the cookie for cf_clearance=*;
                    cf_clearance_cookie = re.search(
                        "cf_clearance=.*?;", message['params']['headers']['set-cookie'])
                    session_cookie = re.search(
                        "__Secure-next-auth.session-token=.*?;", message['params']['headers']['set-cookie'])
                    if cf_clearance_cookie:
                        print("Found Cloudflare Cookie!")
                        # remove the semicolon and 'cf_clearance=' from the string
                        raw_cf_cookie = cf_clearance_cookie.group(0)
                        self.config['cf_clearance'] = raw_cf_cookie.split("=")[1][:-1]
                        if self.debug:
                            print(
                                self.GREEN+"Cloudflare Cookie: "+self.ENDCOLOR + self.config['cf_clearance'])
                        self.cf_cookie_found = True
                    if session_cookie:
                        print("Found Session Token!")
                        # remove the semicolon and '__Secure-next-auth.session-token=' from the string
                        raw_session_cookie = session_cookie.group(0)
                        self.config['session_token'] = raw_session_cookie.split("=")[1][:-1]
                        self.session.cookies.set(
                            "__Secure-next-auth.session-token", self.config["session_token"])
                        if self.debug:
                            print(
                                self.GREEN+"Session Token: "+self.ENDCOLOR + self.config['session_token'])
                        self.session_cookie_found = True
    def detect_user_agent(self, message):
        if 'params' in message:
            if 'headers' in message['params']:
                if 'user-agent' in message['params']['headers']:
                    # Use regex to get the cookie for cf_clearance=*;
                    user_agent = message['params']['headers']['user-agent']
                    self.config['user_agent'] = user_agent
                    self.agent_found = True

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

    def rollback_conversation(self, num=1) -> None:
        """
        Rollback the conversation.
        :param num: The number of messages to rollback
        :return: None
        """
        for i in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()

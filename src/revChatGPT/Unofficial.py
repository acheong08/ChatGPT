import json
import logging
import re
import uuid
from time import sleep

import tls_client
import undetected_chromedriver as uc
from requests.exceptions import HTTPError
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Disable all logging
logging.basicConfig(level=logging.ERROR)

BASE_URL = "https://chat.openai.com/"


class Chrome(uc.Chrome):
    def __del__(self):
        self.quit()


class Chatbot:
    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
        no_refresh=False,
    ) -> None:
        self.config = config
        self.session = tls_client.Session(
            client_identifier="chrome_108",
        )
        if "proxy" in config:
            if type(config["proxy"]) != str:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }
            self.session.proxies.update(proxies)
        if "verbose" in config:
            if type(config["verbose"]) != bool:
                raise Exception("Verbose must be a boolean!")
            self.verbose = config["verbose"]
        else:
            self.verbose = False
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        self.isMicrosoftLogin = False
        # stdout colors
        self.GREEN = "\033[92m"
        self.WARNING = "\033[93m"
        self.ENDCOLOR = "\033[0m"
        if "email" in config and "password" in config:
            if type(config["email"]) != str:
                raise Exception("Email must be a string!")
            if type(config["password"]) != str:
                raise Exception("Password must be a string!")
            self.email = config["email"]
            self.password = config["password"]
            if "isMicrosoftLogin" in config and config["isMicrosoftLogin"] == True:
                self.isMicrosoftLogin = True
                self.__microsoft_login()
            else:
                self.__email_login()
        elif "session_token" in config:
            if no_refresh:
                self.__get_cf_cookies()
                return
            if type(config["session_token"]) != str:
                raise Exception("Session token must be a string!")
            self.session_token = config["session_token"]
            self.session.cookies.set(
                "__Secure-next-auth.session-token",
                config["session_token"],
            )
            self.__get_cf_cookies()
        else:
            raise Exception("Invalid config!")
        self.__retry_refresh()

    def __retry_refresh(self):
        retries = 5
        refresh = True
        while refresh:
            try:
                self.__refresh_session()
                refresh = False
            except Exception as exc:
                if retries == 0:
                    raise exc
                retries -= 1

    def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        gen_title=False,
        session_token=None,
    ):
        """
        Ask a question to the chatbot
        :param prompt: String
        :param conversation_id: UUID
        :param parent_id: UUID
        :param gen_title: Boolean
        :param session_token: String
        """
        if session_token:
            self.session.cookies.set(
                "__Secure-next-auth.session-token",
                session_token,
            )
            self.session_token = session_token
            self.config["session_token"] = session_token
        self.__retry_refresh()
        self.__map_conversations()
        if conversation_id == None:
            conversation_id = self.conversation_id
        if parent_id == None:
            parent_id = (
                self.parent_id
                if conversation_id == self.conversation_id
                else self.conversation_mapping[conversation_id]
            )
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id,
            "parent_message_id": parent_id or str(uuid.uuid4()),
            "model": "text-davinci-002-render"
            if self.config.get("paid") is not True
            else "text-davinci-002-render-paid",
        }
        new_conv = data["conversation_id"] is None
        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=BASE_URL + "backend-api/conversation",
            data=json.dumps(data),
            timeout_seconds=180,
        )
        if response.status_code != 200:
            print(response.text)
            self.__refresh_session()
            raise HTTPError(
                f"Wrong response code: {response.status_code}! Refreshing session...",
            )
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
                res = {
                    "message": message,
                    "conversation_id": self.conversation_id,
                    "parent_id": self.parent_id,
                }
                if gen_title and new_conv:
                    try:
                        title = self.__gen_title(
                            self.conversation_id,
                            self.parent_id,
                        )["title"]
                    except Exception as exc:
                        split = prompt.split(" ")
                        title = " ".join(split[:3]) + ("..." if len(split) > 3 else "")
                    res["title"] = title
                return res
            else:
                return None

    def __check_response(self, response):
        if response.status_code != 200:
            print(response.text)
            raise Exception("Response code error: ", response.status_code)

    def get_conversations(self, offset=0, limit=20):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = BASE_URL + f"backend-api/conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data["items"]

    def get_msg_history(self, id):
        """
        Get message history
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
        response = self.session.get(url)
        self.__check_response(response)
        data = json.loads(response.text)
        return data

    def __gen_title(self, id, message_id):
        """
        Generate title for conversation
        """
        url = BASE_URL + f"backend-api/conversation/gen_title/{id}"
        response = self.session.post(
            url,
            data=json.dumps(
                {
                    "message_id": message_id,
                    "model": "text-davinci-002-render"
                    if self.config.get("paid") is not True
                    else "text-davinci-002-render-paid",
                },
            ),
        )
        self.__check_response(response)
        data = json.loads(response.text)
        return data

    def change_title(self, id, title):
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
        response = self.session.patch(url, data=f'{{"title": "{title}"}}')
        self.__check_response(response)

    def delete_conversation(self, id):
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = BASE_URL + f"backend-api/conversation/{id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def clear_conversations(self):
        """
        Delete all conversations
        """
        url = BASE_URL + "backend-api/conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def __map_conversations(self):
        conversations = self.get_conversations()
        histories = [self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    def __refresh_session(self, session_token=None):
        if session_token:
            self.session.cookies.set(
                "__Secure-next-auth.session-token",
                session_token,
            )
            self.session_token = session_token
            self.config["session_token"] = session_token
        url = BASE_URL + "api/auth/session"
        response = self.session.get(url, timeout_seconds=180)
        if response.status_code == 403:
            self.__get_cf_cookies()
            raise Exception("Clearance refreshing...")
        try:
            if "error" in response.json():
                raise Exception(
                    f"Failed to refresh session! Error: {response.json()['error']}",
                )
            elif (
                response.status_code != 200
                or response.json() == {}
                or "accessToken" not in response.json()
            ):
                raise Exception(
                    f"Response code: {response.status_code} \n Response: {response.text}",
                )
            else:
                self.session.headers.update(
                    {
                        "Authorization": "Bearer " + response.json()["accessToken"],
                    },
                )
            self.session_token = self.session.cookies._find(
                "__Secure-next-auth.session-token",
            )
        except Exception:
            print("Failed to refresh session!")
            if self.isMicrosoftLogin:
                print("Attempting to re-authenticate...")
                self.__microsoft_login()
            else:
                self.__email_login()

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.

        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    def __microsoft_login(self) -> None:
        """
        Login to OpenAI via Microsoft Login Authentication.

        :return: None
        """
        driver = None
        try:
            # Open the browser
            self.cf_cookie_found = False
            self.puid_cookie_found = False
            self.session_cookie_found = False
            self.agent_found = False
            self.cf_clearance = None
            self.puid_cookie = None
            self.user_agent = None
            options = self.__get_ChromeOptions()
            print("Spawning browser...")
            driver = uc.Chrome(
                enable_cdp_events=True,
                options=options,
                driver_executable_path=self.config.get("driver_exec_path"),
                browser_executable_path=self.config.get("browser_exec_path"),
            )
            print("Browser spawned.")
            driver.add_cdp_listener(
                "Network.responseReceivedExtraInfo",
                lambda msg: self.__detect_cookies(msg),
            )
            driver.add_cdp_listener(
                "Network.requestWillBeSentExtraInfo",
                lambda msg: self.__detect_user_agent(msg),
            )
            driver.get(BASE_URL)
            while not self.agent_found or not self.cf_cookie_found:
                sleep(5)
            self.__refresh_headers(
                cf_clearance=self.cf_clearance,
                puid_cookie=self.puid_cookie,
                user_agent=self.user_agent,
            )
            # Wait for the login button to appear
            WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Log in')]"),
                ),
            )
            # Click the login button
            driver.find_element(
                by=By.XPATH,
                value="//button[contains(text(), 'Log in')]",
            ).click()
            # Wait for the Login with Microsoft button to be clickable
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@data-provider='windowslive']"),
                ),
            )
            # Click the Login with Microsoft button
            driver.find_element(
                by=By.XPATH,
                value="//button[@data-provider='windowslive']",
            ).click()
            # Wait for the email input field to appear
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@type='email']"),
                ),
            )
            # Enter the email
            driver.find_element(
                by=By.XPATH,
                value="//input[@type='email']",
            ).send_keys(self.config["email"])
            # Wait for the Next button to be clickable
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='submit']"),
                ),
            )
            # Click the Next button
            driver.find_element(
                by=By.XPATH,
                value="//input[@type='submit']",
            ).click()
            # Wait for the password input field to appear
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@type='password']"),
                ),
            )
            # Enter the password
            driver.find_element(
                by=By.XPATH,
                value="//input[@type='password']",
            ).send_keys(self.config["password"])
            # Wait for the Sign in button to be clickable
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='submit']"),
                ),
            )
            # Click the Sign in button
            driver.find_element(
                by=By.XPATH,
                value="//input[@type='submit']",
            ).click()
            # Wait for the Allow button to appear
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='submit']"),
                ),
            )
            # click Yes button
            driver.find_element(
                by=By.XPATH,
                value="//input[@type='submit']",
            ).click()
            # wait for input box to appear (to make sure we're signed in)
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//textarea"),
                ),
            )
            while not self.session_cookie_found:
                sleep(5)
            print(self.GREEN + "Login successful." + self.ENDCOLOR)
        finally:
            # Close the browser
            if driver is not None:
                driver.quit()
                del driver

    def __email_login(self) -> None:
        """
        Login to OpenAI via Email/Password Authentication and 2Captcha.

        :return: None
        """
        # Open the browser
        driver = None
        try:
            self.cf_cookie_found = False
            self.puid_cookie_found = False
            self.session_cookie_found = False
            self.agent_found = False
            self.cf_clearance = None
            self.puid_cookie = None
            self.user_agent = None
            options = self.__get_ChromeOptions()
            print("Spawning browser...")
            driver = uc.Chrome(
                enable_cdp_events=True,
                options=options,
                driver_executable_path=self.config.get("driver_exec_path"),
                browser_executable_path=self.config.get("browser_exec_path"),
            )
            print("Browser spawned.")
            driver.add_cdp_listener(
                "Network.responseReceivedExtraInfo",
                lambda msg: self.__detect_cookies(msg),
            )
            driver.add_cdp_listener(
                "Network.requestWillBeSentExtraInfo",
                lambda msg: self.__detect_user_agent(msg),
            )
            driver.get(BASE_URL)
            while not self.agent_found or not self.cf_cookie_found:
                sleep(5)
            self.__refresh_headers(
                cf_clearance=self.cf_clearance,
                puid_cookie=self.puid_cookie,
                user_agent=self.user_agent,
            )
            # Wait for the login button to appear
            WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Log in')]"),
                ),
            )
            # Click the login button
            driver.find_element(
                by=By.XPATH,
                value="//button[contains(text(), 'Log in')]",
            ).click()
            # Wait for the email input field to appear
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.ID, "username"),
                ),
            )
            # Enter the email
            driver.find_element(by=By.ID, value="username").send_keys(
                self.config["email"],
            )
            # Wait for the Continue button to be clickable
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@type='submit']"),
                ),
            )
            # Click the Continue button
            driver.find_element(
                by=By.XPATH,
                value="//button[@type='submit']",
            ).click()
            # Wait for the password input field to appear
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.ID, "password"),
                ),
            )
            # Enter the password
            driver.find_element(by=By.ID, value="password").send_keys(
                self.config["password"],
            )
            # Wait for the Sign in button to be clickable
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@type='submit']"),
                ),
            )
            # Click the Sign in button
            driver.find_element(
                by=By.XPATH,
                value="//button[@type='submit']",
            ).click()
            # wait for input box to appear (to make sure we're signed in)
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//textarea"),
                ),
            )
            while not self.session_cookie_found or not self.puid_cookie_found:
                sleep(5)
            print(self.GREEN + "Login successful." + self.ENDCOLOR)
        finally:
            if driver is not None:
                # Close the browser
                driver.quit()
                del driver

    def __get_ChromeOptions(self):
        options = uc.ChromeOptions()
        options.add_argument("--start_maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if self.config.get("proxy", "") != "":
            options.add_argument("--proxy-server=" + self.config["proxy"])
        return options

    def __get_cf_cookies(self) -> None:
        """
        Get cloudflare cookies.

        :return: None
        """
        driver = None
        try:
            self.cf_cookie_found = False
            self.agent_found = False
            self.puid_cookie_found = False
            self.cf_clearance = None
            self.puid_cookie = None
            self.user_agent = None
            options = self.__get_ChromeOptions()
            print("Spawning browser...")
            driver = uc.Chrome(
                enable_cdp_events=True,
                options=options,
                driver_executable_path=self.config.get("driver_exec_path"),
                browser_executable_path=self.config.get("browser_exec_path"),
            )
            print("Browser spawned.")
            driver.add_cdp_listener(
                "Network.responseReceivedExtraInfo",
                lambda msg: self.__detect_cookies(msg),
            )
            driver.add_cdp_listener(
                "Network.requestWillBeSentExtraInfo",
                lambda msg: self.__detect_user_agent(msg),
            )
            driver.get("https://chat.openai.com/chat")
            while (
                not self.agent_found
                or not self.cf_cookie_found
                or not self.puid_cookie_found
            ):
                sleep(5)
        finally:
            # Close the browser
            if driver is not None:
                driver.quit()
                del driver
            self.__refresh_headers(
                cf_clearance=self.cf_clearance,
                puid_cookie=self.puid_cookie,
                user_agent=self.user_agent,
            )

    def __detect_cookies(self, message):
        if "params" in message:
            if "headers" in message["params"]:
                if "set-cookie" in message["params"]["headers"]:
                    # Use regex to get the cookie for cf_clearance=*;
                    cf_clearance_cookie = re.search(
                        "cf_clearance=.*?;",
                        message["params"]["headers"]["set-cookie"],
                    )
                    puid_cookie = re.search(
                        "_puid=.*?;",
                        message["params"]["headers"]["set-cookie"],
                    )
                    session_cookie = re.search(
                        "__Secure-next-auth.session-token=.*?;",
                        message["params"]["headers"]["set-cookie"],
                    )
                    if cf_clearance_cookie and not self.cf_cookie_found:
                        print("Found Cloudflare Cookie!")
                        # remove the semicolon and 'cf_clearance=' from the string
                        raw_cf_cookie = cf_clearance_cookie.group(0)
                        self.cf_clearance = raw_cf_cookie.split("=")[1][:-1]
                        if self.verbose:
                            print(
                                self.GREEN
                                + "Cloudflare Cookie: "
                                + self.ENDCOLOR
                                + self.cf_clearance,
                            )
                        self.cf_cookie_found = True
                    if puid_cookie and not self.puid_cookie_found:
                        raw_puid_cookie = puid_cookie.group(0)
                        self.puid_cookie = raw_puid_cookie.split("=")[1][:-1]
                        self.session.cookies.set(
                            "_puid",
                            self.puid_cookie,
                        )
                        if self.verbose:
                            print(
                                self.GREEN
                                + "puid Cookie: "
                                + self.ENDCOLOR
                                + self.puid_cookie,
                            )
                        self.puid_cookie_found = True
                    if session_cookie and not self.session_cookie_found:
                        print("Found Session Token!")
                        # remove the semicolon and '__Secure-next-auth.session-token=' from the string
                        raw_session_cookie = session_cookie.group(0)
                        self.session_token = raw_session_cookie.split("=")[1][:-1]
                        self.session.cookies.set(
                            "__Secure-next-auth.session-token",
                            self.session_token,
                        )
                        if self.verbose:
                            print(
                                self.GREEN
                                + "Session Token: "
                                + self.ENDCOLOR
                                + self.session_token,
                            )
                        self.session_cookie_found = True

    def __detect_user_agent(self, message):
        if "params" in message:
            if "headers" in message["params"]:
                if "user-agent" in message["params"]["headers"]:
                    # Use regex to get the cookie for cf_clearance=*;
                    user_agent = message["params"]["headers"]["user-agent"]
                    self.user_agent = user_agent
                    self.agent_found = True
        self.__refresh_headers(
            cf_clearance=self.cf_clearance,
            puid_cookie=self.puid_cookie,
            user_agent=self.user_agent,
        )

    def __refresh_headers(self, cf_clearance, puid_cookie, user_agent):
        del self.session.cookies["cf_clearance"]
        del self.session.cookies["_puid"]
        self.session.headers.clear()
        self.session.cookies.set("cf_clearance", cf_clearance)
        self.session.cookies.set("_puid", puid_cookie)
        self.session.headers.update(
            {
                "Accept": "text/event-stream",
                "Authorization": "Bearer ",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "X-Openai-Assistant-App-Id": "",
                "Connection": "close",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://chat.openai.com/chat",
            },
        )

    def rollback_conversation(self, num=1) -> None:
        """
        Rollback the conversation.
        :param num: The number of messages to rollback
        :return: None
        """
        for i in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()


def get_input(prompt):
    # Display the prompt
    print(prompt, end="")

    # Initialize an empty list to store the input lines
    lines = []

    # Read lines of input until the user enters an empty line
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    # Join the lines, separated by newlines, and store the result
    user_input = "\n".join(lines)

    # Return the input
    return user_input


from os import getenv
from os.path import exists


def configure():
    config_files = ["config.json"]
    xdg_config_home = getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
    user_home = getenv("HOME")
    if user_home:
        config_files.append(f"{user_home}/.config/revChatGPT/config.json")

    config_file = next((f for f in config_files if exists(f)), None)
    if config_file:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("No config file found.")
        raise Exception("No config file found.")
    return config


def chatGPT_main(config):
    print("Logging in...")
    chatbot = Chatbot(config)
    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if prompt == "!help":
                print(
                    """
                !help - Show this message
                !reset - Forget the current conversation
                !refresh - Refresh the session authentication
                !config - Show the current configuration
                !rollback x - Rollback the conversation (x being the number of messages to rollback)
                !exit - Exit this program
                """,
                )
                continue
            elif prompt == "!reset":
                chatbot.reset_chat()
                print("Chat session successfully reset.")
                continue
            elif prompt == "!refresh":
                chatbot.__refresh_session()
                print("Session successfully refreshed.\n")
                continue
            elif prompt == "!config":
                print(json.dumps(chatbot.config, indent=4))
                continue
            elif prompt.startswith("!rollback"):
                # Default to 1 rollback if no number is specified
                try:
                    rollback = int(prompt.split(" ")[1])
                except IndexError:
                    rollback = 1
                chatbot.rollback_conversation(rollback)
                print(f"Rolled back {rollback} messages.")
                continue
            elif prompt.startswith("!setconversation"):
                try:
                    chatbot.config["conversation"] = prompt.split(" ")[1]
                    print("Conversation has been changed")
                except IndexError:
                    print("Please include conversation UUID in command")
                continue
            elif prompt == "!exit":
                break
        try:
            print("Chatbot: ")
            message = chatbot.ask(
                prompt,
                conversation_id=chatbot.config.get("conversation"),
                parent_id=chatbot.config.get("parent_id"),
            )
            print(message["message"])
        except Exception as exc:
            print("Something went wrong!")
            print(exc)
            continue


def main():
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    chatGPT_main(configure())


if __name__ == "__main__":
    main()

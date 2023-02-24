"""
Standard ChatGPT
"""
import json
import logging
import uuid

from V1Base import V1BaseClass, BASE_URL, get_input, configure, logger, Error, log


class Chatbot(V1BaseClass):
    """
    Chatbot class for ChatGPT
    """

    @logger(is_timed=True)
    def __init__(
        self,
        config,
        conversation_id=None,
        parent_id=None,
    ) -> None:
        super().__init__(
            config,
            conversation_id=conversation_id,
            parent_id=parent_id,
        )

    @logger(is_timed=True)
    def ask(
        self,
        prompt,
        conversation_id=None,
        parent_id=None,
        timeout=360,
        # gen_title=True,
    ):
        """
        Ask a question to the chatbot
        :param prompt: String
        :param conversation_id: UUID
        :param parent_id: UUID
        :param gen_title: Boolean
        """
        if parent_id is not None and conversation_id is None:
            log.error("conversation_id must be set once parent_id is set")
            error = Error()
            error.source = "User"
            error.message = "conversation_id must be set once parent_id is set"
            error.code = -1
            raise error
            # user-specified covid and parid, check skipped to avoid rate limit

        if (
            conversation_id is not None and conversation_id != self.conversation_id
        ):  # Update to new conversations
            log.debug("Updating to new conversation by setting parent_id to None")
            self.parent_id = None  # Resetting parent_id

        conversation_id = conversation_id or self.conversation_id
        parent_id = parent_id or self.parent_id
        if conversation_id is None and parent_id is None:  # new conversation
            parent_id = str(uuid.uuid4())
            log.debug("New conversation, setting parent_id to new UUID4: %s", parent_id)

        if conversation_id is not None and parent_id is None:
            if conversation_id not in self.conversation_mapping:
                # Use lazy % formatting in logging functionspylint(logging-fstring-interpolation)

                log.debug(
                    "Conversation ID %s not found in conversation mapping, mapping conversations",
                    conversation_id,
                )

                self.__map_conversations()
            log.debug(
                "Conversation ID %s found in conversation mapping, setting parent_id to %s",
                conversation_id,
                self.conversation_mapping[conversation_id],
            )
            parent_id = self.conversation_mapping[conversation_id]
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
            "parent_message_id": parent_id,
            "model": "text-davinci-002-render-sha"
            if not self.config.get("paid")
            else "text-davinci-002-render-paid",
        }
        log.debug("Sending the payload")
        log.debug(json.dumps(data, indent=2))
        # new_conv = data["conversation_id"] is None
        self.conversation_id_prev_queue.append(
            data["conversation_id"],
        )  # for rollback
        self.parent_id_prev_queue.append(data["parent_message_id"])
        response = self.session.post(
            url=BASE_URL + "api/conversation",
            data=json.dumps(data),
            timeout=timeout,
            stream=True,
        )
        self.check_response(response)
        for line in response.iter_lines():
            line = str(line)[2:-1]
            if line == "Internal Server Error":
                log.error("Internal Server Error: %s", line)
                raise Exception("Error: " + str(line))
            if line == "" or line is None:
                continue
            if "data: " in line:
                line = line[6:]
            if line == "[DONE]":
                break

            # Replace accidentally escaped double quotes
            line = line.replace('\\"', '"')
            line = line.replace("\\'", "'")
            line = line.replace("\\\\", "\\")
            # Try parse JSON
            try:
                line = json.loads(line)
            except json.decoder.JSONDecodeError:
                log.info("Error parsing JSON")
                continue
            if not self.check_fields(line):
                log.error("Field missing", exc_info=True)
                if (
                    line.get("details")
                    == "Too many requests in 1 hour. Try again later."
                ):
                    log.error("Rate limit exceeded")
                    raise Error(source="ask", message=line.get("details"), code=2)
                raise Error(source="ask", message="Field missing", code=1)

            message = line["message"]["content"]["parts"][0]
            conversation_id = line["conversation_id"]
            parent_id = line["message"]["id"]
            log.debug("Received message: %s", message)
            log.debug("Received conversation_id: %s", conversation_id)
            log.debug("Received parent_id: %s", parent_id)
            yield {
                "message": message,
                "conversation_id": conversation_id,
                "parent_id": parent_id,
            }
        self.conversation_mapping[conversation_id] = parent_id
        if parent_id is not None:
            self.parent_id = parent_id
        if conversation_id is not None:
            self.conversation_id = conversation_id

    @logger(is_timed=True)
    def get_conversations(self, offset=0, limit=20):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = BASE_URL + f"api/conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.check_response(response)
        data = json.loads(response.text)
        return data["items"]

    @logger(is_timed=True)
    def get_msg_history(self, convo_id, encoding=None):
        """
        Get message history
        :param id: UUID of conversation
        :param encoding: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.get(url)
        self.check_response(response)
        if encoding is not None:
            response.encoding = encoding
        data = json.loads(response.text)
        return data

    @logger(is_timed=True)
    def gen_title(self, convo_id, message_id):
        """
        Generate title for conversation
        """
        url = BASE_URL + f"api/conversation/gen_title/{convo_id}"
        response = self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        self.check_response(response)

    @logger(is_timed=True)
    def change_title(self, convo_id, title):
        """
        Change title of conversation
        :param id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data=json.dumps({"title": title}))
        self.check_response(response)

    @logger(is_timed=True)
    def delete_conversation(self, convo_id):
        """
        Delete conversation
        :param id: UUID of conversation
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.check_response(response)

    @logger(is_timed=True)
    def clear_conversations(self):
        """
        Delete all conversations
        """
        url = BASE_URL + "api/conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.check_response(response)

    @logger(is_timed=False)
    def __map_conversations(self):
        conversations = self.get_conversations()
        histories = [self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]


@logger(is_timed=False)
def main(config: dict):
    """
    Main function for the chatGPT program.
    """
    print("Logging in...")
    chatbot = Chatbot(
        config,
        conversation_id=config.get("conversation_id"),
        parent_id=config.get("parent_id"),
    )

    def handle_commands(command: str) -> bool:
        if command == "!help":
            print(
                """
            !help - Show this message
            !reset - Forget the current conversation
            !config - Show the current configuration
            !rollback x - Rollback the conversation (x being the number of messages to rollback)
            !exit - Exit this program
            !setconversation - Changes the conversation
            """,
            )
        elif command == "!reset":
            chatbot.reset_chat()
            print("Chat session successfully reset.")
        elif command == "!config":
            print(json.dumps(chatbot.config, indent=4))
        elif command.startswith("!rollback"):
            # Default to 1 rollback if no number is specified
            try:
                rollback = int(command.split(" ")[1])
            except IndexError:
                logging.exception(
                    "No number specified, rolling back 1 message",
                    stack_info=True,
                )
                rollback = 1
            chatbot.rollback_conversation(rollback)
            print(f"Rolled back {rollback} messages.")
        elif command.startswith("!setconversation"):
            try:
                chatbot.conversation_id = chatbot.config[
                    "conversation_id"
                ] = command.split(" ")[1]
                print("Conversation has been changed")
            except IndexError:
                log.exception(
                    "Please include conversation UUID in command",
                    stack_info=True,
                )
                print("Please include conversation UUID in command")
        elif command == "!exit":
            exit(0)
        else:
            return False
        return True

    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if handle_commands(prompt):
                continue

        print("Chatbot: ")
        prev_text = ""
        for data in chatbot.ask(
            prompt,
        ):
            message = data["message"][len(prev_text) :]
            print(message, end="", flush=True)
            prev_text = data["message"]
        print()
        # print(message["message"])


if __name__ == "__main__":
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    main(configure())

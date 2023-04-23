import asyncio
import datetime

import revChatGPT.V1
from revChatGPT.recipient import PythonRecipient
from revChatGPT.V1 import Chatbot


def test_recipient():
    """
    Test the chatbot
    """
    config = revChatGPT.V1.configure()
    assert "access_token" in config
    cbt = Chatbot(config)
    assert cbt is not None

    # Try to get the recipient which is not registered
    try:
        _ = cbt.recipients["python"]
        assert False
    except Exception as ex:
        assert isinstance(ex, KeyError)
        assert ex.args[0] == "Recipient 'python' is not registered."

    # Register the recipient
    cbt.recipients["python"] = PythonRecipient
    assert cbt.recipients["python"].DESCRIPTION == "Python Interpreter Remote"

    # Try to register the recipient which is already registered
    try:
        cbt.recipients["python"] = PythonRecipient
        assert False
    except Exception as ex:
        assert isinstance(ex, KeyError)
        assert ex.args[0] == "Recipient 'python' is already registered."

    # To get the recipient instance
    python = cbt.recipients["python"]()

    api_docs = f"""

    Knowledge cutoff: 2021-09
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    ###Available Tools:
    python

    {python.API_DOCS}
    """
    for _ in cbt.ask("You are ChatGPT." + api_docs):
        pass

    # Test the python recipient
    result = {}
    for _ in cbt.ask("Please calculate 27! + 8! by using python."):
        result = _
    assert result
    assert not result["end_turn"]

    times = 0
    while not result.get("end_turn", True):
        times += 1
        recipient_name = result["recipient"]
        if times >= 3:
            break
        assert recipient_name == "python"
        msg = asyncio.get_event_loop().run_until_complete(
            python.aprocess(message=result.copy()),
        )
        assert msg["content"]["parts"][0].startswith("```")
        for _ in cbt.post_messages([msg]):
            result = _

    assert times == 1
    assert "10888869450418352160768040320" in result["message"].replace(",", "")

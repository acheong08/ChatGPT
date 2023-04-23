# Recipient Framework

This module provides a framework for managing recipients. It defines three class `Recipient`, `RecipientManager` and `PythonRecipient`. It also defines a metaclass `RecipientMeta` for the `Recipient` class.

`Recipient` is an abstract base class that defines the basic structure and methods for a recipient. It provides an interface for processing a message and an asynchronous processing method, along with a UUID generator for generating unique message IDs.

`RecipientManager` is a class that manages a registry of recipients. It allows users to register and unregister recipients by name, and provides an interface for accessing and retrieving registered recipients. The class also provides a property for listing all available recipients, along with their descriptions.

`PythonRecipient` is a class that provides an interface for processing Python code. It provides an asynchronous context manager for executing code in a separate thread, and an asynchronous processing method for processing messages.

`RecipientMeta` is a metaclass for the `Recipient` class. It sets the `RECIPIENT_NAME` attribute of the class to the name of the class, if the attribute is not already set.

## Example usage

More detail on the usage of the recipient framework can be found in the ./tests/test_recipient.py file.

### Defining a custom recipient

```python
# Define a custom recipient by extending the Recipient base class
class CustomRecipient(Recipient):
    def process(self, message: dict, **kwargs: dict) -> dict:
        # Custom message processing logic here
        return {
            "id": self._uuid(),
            "author": {
                "role": "tool",
                "name": self.RECIPIENT_NAME,
            },
            "content": {"content_type": "text", "parts": ["success"]},
        }
    async def aprocess(self, message: dict, **kwargs: dict) -> dict:
        raise NotImplementedError("Please call the process method instead.")

# Create a recipient manager instance
manager = RecipientManager()
# Register the custom recipient with the manager using the __setitem__ method
manager["custom"] = CustomRecipient()

# Register the custom recipient with the manager using the @manager.register decorator
@manager.register("another_custom")
class AsyncCustomRecipient(CustomRecipient):
    async def aprocess(self, message: dict, **kwargs: dict) -> dict:
        # Custom asynchronous message processing logic here
        return {
            "id": self._uuid(),
            "author": {
                "role": "tool",
                "name": self.RECIPIENT_NAME,
            },
            "content": {"content_type": "text", "parts": ["success"]},
        }

# Retrieve the custom recipient from the manager
custom_recipient = manager["custom"]
# Get a list of all available recipients
available_recipients = manager.available_recipients
```

### How to use

```python
... Assume that the cbt was configured correctly ...

# Register the recipient
cbt.recipients["python"] = PythonRecipient
# To get the recipient instance
python = cbt.recipients["python"]()

# Create API Docs
api_docs = f"""

Knowledge cutoff: 2021-09
Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

###Available Tools:
python

{python.API_DOCS}
"""
# To notify the assistant that the recipient is ready
for _ in cbt.ask("You are ChatGPT." + api_docs):
    pass
result = {}

# Now, ask GPT to calculate 27! + 8! by using the python recipient
for _ in cbt.ask("Please calculate 27! + 8! by using python."):
    result = _

times = 0
# "end_turn" is a flag that indicates whether the GPT has finished the work.
# If the flag is False, it means that the GPT needs to use the recipient to help it.
# If the flag is True, it means that the GPT has finished the work.
while not result.get("end_turn", True):
    times += 1
    # Get the name of the recipient
    recipient_name = result["recipient"]
    # To avoid the endless loop.
    if times >= 3:
        break

    # This process could be managed by a class, but I don't finish it yet.
    if recipient_name == "python":
        # To get the result of executing the code
        msg = asyncio.get_event_loop().run_until_complete(
            python.aprocess(message=result.copy())
        )

    # To send the result to the GPT
    for _ in cbt.post_messages([msg]):
        result = _

# Now the GPT has finished the work.
print(result['message'])
# The GPT will calculate 27! + 8! correctly.
```

## RecipientMeta

A metaclass for the `Recipient` class. It sets the `RECIPIENT_NAME` attribute of the class to the name of the class, if the attribute is not already set.

### Methods

- `__new__(mcs, name, bases, namespace, /, **kwargs)`

## Recipient

The base class for recipients.

### Attributes

- `DESCRIPTION : str` : A description of the recipient for humans.
- `API_DOCS : str` : Documentation of the recipient for machines.
- `REQUIRED_ARGS : list` : A list of required parameters.
- `EXAMPLE_MESSAGES : list` : A list of example messages.
- `RECIPIENT_NAME : str` : The name of the recipient. Defaults to the class name.

### Methods

- `process(message: dict, **kwargs: dict) -> dict` : Process a message.
- `aprocess(message: dict, **kwargs: dict) -> dict` : Asynchronously process a message.

## RecipientManager

A class for managing recipients.

### Methods

- `register(name: str) -> Callable[[Type[Recipient]], Type[Recipient]]` : Decorator for registering a recipient to the manager.
- `__getitem__(name: str) -> Type[Recipient]` : Get a recipient from the manager.
- `__setitem__(name: str, recipient_class: Type[Recipient])` : Register a recipient to the manager.
- `__delitem__(name: str)` : Unregister a recipient from the manager.

### Properties

- `available_recipients : dict[str, str]` : A dictionary containing the available recipients.

## PythonRecipient

A class for processing Python code.

### Attributes

- `DESCRIPTION : str` : A description of the Python recipient for humans.
- `API_DOCS : str` : Documentation of the Python recipient for machines.
- `RECIPIENT_NAME : str` : The name of the Python recipient.

### Methods

- `process(message: dict, **kwargs: dict) -> dict` : Not implemented. PythonRecipient is asynchronous only.
- `aprocess(message: dict, **kwargs: dict) -> dict` : Asynchronously process a message. It will execute the code in the `message` in Tio.
- `_uuid() -> str` : Generate a UUID.
- `__aenter__() -> PythonRecipient` : Enter the PythonRecipient async context manager.
- `__aexit__(exc_type, exc_val, exc_tb) -> None` : Exit the PythonRecipient async context manager.

"""
This module provides a framework for managing recipients. It defines three class
`Recipient`, `RecipientManager` and `PythonRecipient`. It also defines a metaclass
`RecipientMeta` for the `Recipient` class.

`Recipient` is an abstract base class that defines the basic structure and methods
for a recipient. It provides an interface for processing a message and an
asynchronous processing method, along with a UUID generator for generating unique
message IDs.

`RecipientManager` is a class that manages a registry of recipients. It allows users
to register and unregister recipients by name, and provides an interface for
accessing and retrieving registered recipients. The class also provides a property
for listing all available recipients, along with their descriptions.

`PythonRecipient` is a class that provides an interface for processing Python code.
It provides an asynchronous context manager for executing code in a separate thread,
and an asynchronous processing method for processing messages.

`RecipientMeta` is a metaclass for the `Recipient` class. It sets the `RECIPIENT_NAME`
attribute of the class to the name of the class, if the attribute is not already set.
"""
import asyncio
import uuid
from abc import ABCMeta
from abc import abstractmethod
from typing import Callable
from typing import Type

from async_tio import Tio


class RecipientMeta(ABCMeta):
    """
    Metaclass for the Recipient class.
    """

    def __new__(mcs, name, bases, namespace, /, **kwargs):
        if not "RECIPIENT_NAME" in namespace or not namespace["RECIPIENT_NAME"]:
            namespace["RECIPIENT_NAME"] = name
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        return cls


class Recipient(metaclass=RecipientMeta):
    """
    Recipient base class.

    Attributes
    ----------
    DESCRIPTION : str
        Description of the recipient for humans.
    API_DOCS : str
        Documentation of the recipient for machines.
    REQUIRED_ARGS : list
        List of required parameters.
    EXAMPLE_MESSAGES : list
        List of example messages.
    RECIPIENT_NAME : str
        Name of the recipient. Defaults to the class name.

    Methods
    -------
    process(message: dict, **kwargs: dict)
        Process a message.
    aprocess(message: dict, **kwargs: dict)
        Asynchronously process a message.
    """

    DESCRIPTION = ""
    API_DOCS = ""
    REQUIRED_ARGS = []
    EXAMPLE_MESSAGES = []
    RECIPIENT_NAME = ""
    # Defaults to the class name. This process is handled by the metaclass.

    @abstractmethod
    def process(self, message: dict, **kwargs: dict) -> dict:
        """
        Process a message.

        Parameters
        ----------
        message : dict
            The message to process.
        kwargs : dict
            Additional arguments.

        Returns
        -------
        dict
            The message which need to be sent.
        """
        raise NotImplementedError("Method needs to be implemented in subclass.")

    @abstractmethod
    async def aprocess(self, message: dict, **kwargs: dict) -> dict:
        """
        Asynchronously process a message.

        Parameters
        ----------
        message : dict
            The message to process.
        kwargs : dict
            Additional arguments.

        Returns
        -------
        dict
            The message which need to be sent.
        """
        raise NotImplementedError("Method needs to be implemented in subclass.")

    def _uuid(self) -> str:
        """
        Generate a UUID.

        Returns
        -------
        str
            A UUID.
        """
        return str(uuid.uuid4())


class RecipientManager:
    """Recipient Manager class.

    Methods
    -------
    register(name: str) -> Callable[[Type[Recipient]], Type[Recipient]]
        Decorator for registering a recipient to the manager.
    __getitem__(name: str) -> Type[Recipient]
        Get a recipient from the manager.
    __setitem__(name: str, recipient_class: Type[Recipient])
        Register a recipient to the manager.
    __delitem__(name: str)
        Unregister a recipient from the manager.

    Properties
    ----------
    available_recipients : dict[str, str]
        Dictionary containing the available recipients.
    """

    def __init__(self):
        self.__registry_list = {}

    def register(self, name="") -> Callable[[Type[Recipient]], Type[Recipient]]:
        """Decorator for registering a recipient to the manager.

        Parameters
        ----------
        name : str
            The name of the recipient to register.

        Returns
        -------
        Callable[[Type[Recipient]], Type[Recipient]]
            Decorator function for registering the recipient.
        """

        def decorator(recipient_class: Type[Recipient]) -> Type[Recipient]:
            self[name or recipient_class.RECIPIENT_NAME] = recipient_class
            return recipient_class

        return decorator

    @property
    def available_recipients(self) -> dict[str, str]:
        """Dictionary containing the available recipients.

        Returns
        -------
        dict[str, str]
            A dictionary where the keys are the names of the available recipients, and
            the values are their descriptions.
        """
        return {
            name: recipient_class.DESCRIPTION
            for name, recipient_class in self.__registry_list.items()
        }

    def __getitem__(self, name: str) -> Type[Recipient]:
        """Get a recipient from the manager.

        Parameters
        ----------
        name : str
            The name of the recipient to get.

        Returns
        -------
        Type[Recipient]
            The recipient class.

        Raises
        ------
        KeyError
            Raised if the recipient is not registered.
        """
        if name not in self.__registry_list:
            raise KeyError(f"Recipient '{name}' is not registered.")
        return self.__registry_list[name]

    def __setitem__(self, name: str, recipient_class: Type[Recipient]):
        """Register a recipient to the manager.

        Parameters
        ----------
        name : str
            The name of the recipient to set.
        recipient_class : Type[Recipient]
            The class of the recipient to set.

        Raises
        ------
        KeyError
            Raised if the recipient is already registered.
        """
        if name in self.__registry_list:
            raise KeyError(f"Recipient '{name}' is already registered.")
        self.__registry_list[name] = recipient_class

    def __delitem__(self, name: str):
        """Unregister a recipient from the manager.

        Parameters
        ----------
        name : str
            The name of the recipient to unregister.
        """
        del self.__registry_list[name]

    def __contains__(self, name: str) -> bool:
        """Check if a recipient is registered.

        Parameters
        ----------
        name : str
            The name of the recipient to check.

        Returns
        -------
        bool
            True if the recipient is registered, False otherwise.
        """
        return name in self.__registry_list


class PythonRecipient(Recipient):
    """
    Python recipient class.
    """

    DESCRIPTION = "Python Interpreter Remote"
    API_DOCS = (
        "You have the tool python, and you can run any python code because it run in a sandbox.\n"
        "But you must send the code to recipient 'python' to run it."
    )
    RECIPIENT_NAME = "python"
    # Because OpenAI has finetuned GPT-3.5 to use python, we don't need examples.

    def __init__(self) -> None:
        super().__init__()
        self.tio = Tio()

    async def aprocess(self, message: dict, **kwargs: dict):
        result = await self.tio.execute(message["message"], language="python3")
        result = result.stdout[:-1]
        return {
            "id": self._uuid(),
            "author": {
                "role": "tool",
                "name": self.RECIPIENT_NAME,
            },
            "content": {
                "content_type": "text",
                "parts": [f"```output\n{result}\n```"],
            },
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.tio.close()

    def process(self, message: dict, **kwargs: dict) -> dict:
        return asyncio.get_event_loop().run_until_complete(
            self.aprocess(message, **kwargs),
        )

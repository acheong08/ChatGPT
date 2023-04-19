"""
The __init__ file does not a main file

You can import the following module to use:
revChatGPT.V0
revChatGPT.V1
revChatGPT.V3
"""
__version__ = "4.2.4"
__all__ = ()

# Available Python Version Verify
from . import typings as t
from platform import python_version_tuple
from platform import python_version
from warnings import warn

versions = [int(v) for v in python_version_tuple()]
if versions[0] < 3:
    error = t.NotAllowRunning("Not available Python version")
    raise error
elif versions[1] < 9:
    error = t.NotAllowRunning(f"Not available Python version: {python_version()}")
    raise error
else:
    if versions[1] < 10 and versions[0] == 3:
        warning = UserWarning(
            "The current Python is not a recommended version, 3.10+ is recommended",
        )
        warn(warning)
        del warning
    del t, python_version, python_version_tuple, versions, warn

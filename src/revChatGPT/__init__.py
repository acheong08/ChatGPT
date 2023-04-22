"""
The __init__ file does not a main file

You can import the following module to use:
revChatGPT.V1
revChatGPT.V3
"""
__version__ = "4.2.4"
__all__ = ()

# Available Python Version Verify
from . import typings as t

if __import__('platform').python_version_tuple()[0] < 3:
    error = t.NotAllowRunning("Not available Python version")
    raise error
elif __import__('platform').python_version_tuple()[1] < 9:
    error = t.NotAllowRunning(f"Not available Python version: {__import__('platform').python_version()}")
    raise error
else:
    if __import__('platform').python_version_tuple()[1] < 10 and __import__('platform').python_version_tuple()[0] == 3:
        from warnings import warn
        warning = UserWarning(
            "The current Python is not a recommended version, 3.10+ is recommended",
        )
        warn(warning)
        del warning, warn
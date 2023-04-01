# Available Python Version Verify
from . import typings as t
from platform import python_version_tuple
from platform import python_version
versions = [int(v) for v in python_version_tuple()]
if versions[0] < 3:
    error = t.NotAllowRunning("Not available Python version")
    raise error
elif versions[1] < 9:
    error = t.NotAllowRunning(f"Not available Python version: {python_version()}")
    raise error
else:
    del t, python_version, python_version_tuple, versions

from setuptools import setup, find_packages
setup(
    name = "ChatGPT",
    version = "0.0.1",
    packages = find_packages(),
    license = "GNU General Public License v2.0",
    author = "Antonio Cheong",
    author_email = "acheong@student.dalat.org",
    description = "ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    url = "https://github.com/acheong08/ChatGPT",
    install_requires = [
        "requests"
    ]
)

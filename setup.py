from setuptools import find_packages
from setuptools import setup

setup(
    name="revChatGPT",
    version="3.1.1",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/acheong08/ChatGPT",
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    license="GNU General Public License v2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["Unofficial", "V2", "V1", "V0", "V3"],
    install_requires=[
        "OpenAIAuth==0.3.2",
        "requests[socks]",
        "httpx[socks]",
        "prompt-toolkit",
        "tiktoken",
    ],
    extras_require={
        "unofficial": [
            "requests",
            "undetected_chromedriver",
            "selenium",
            "tls_client",
        ],
        "official": [
            "openai",
            "tiktoken",
        ],
    },
)

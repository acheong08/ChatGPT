from setuptools import find_packages
from setuptools import setup

setup(
    name="revChatGPT",
    version="0.0.44.1",
    license="GNU General Public License v2.0",
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["revChatGPT"],
    url="https://github.com/ChatGPT-Hackers/revChatGPT",
    install_requires=[
        "httpx",
        "nest-asyncio",
        "OpenAIAuth>=0.0.6",
        "playwright",
        "cf_clearance2>=0.28.3",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "revChatGPT = revChatGPT.__main__:main",
        ]
    },
)

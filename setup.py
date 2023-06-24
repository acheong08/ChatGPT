from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

DOCS_PATH = Path(__file__).parents[0] / "docs/README.md"
PATH = Path("README.md")
if not PATH.exists():
    with open(DOCS_PATH, encoding="utf-8") as f1:
        with open(PATH, "w+", encoding="utf-8") as f2:
            f2.write(f1.read())

setup(
    name="revChatGPT",
    version="6.4.2",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    long_description=open(PATH, encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/acheong08/ChatGPT",
    project_urls={
        "Bug Report": "https://github.com/acheong08/ChatGPT/issues/new?assignees=&labels=bug-report&template=bug_report.yml&title=%5BBug%5D%3A+",
        "Feature request": "https://github.com/acheong08/ChatGPT/issues/new?assignees=&labels=enhancement&template=feature_request.yml&title=%5BFeature+Request%5D%3A+",
    },
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    license="GNU General Public License v2.0",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    py_modules=["revChatGPT"],
    package_data={"": ["*.json"]},
    install_requires=[
        "OpenAIAuth>=1.0.2",
        "requests[socks]",
        "httpx[socks]",
        "async_tio",
        "prompt-toolkit",
        "tiktoken>=0.3.0",
        "openai",
        "curl_cffi",
        "rich",
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

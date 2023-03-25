from setuptools import find_namespace_packages
from setuptools import setup

setup(
    name="revChatGPT",
    version="4.0.9",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    long_description=open("README.md", encoding="utf-8").read(),
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
    py_modules=["V2", "V1", "V0", "V3"],
    package_data={"": ["*.json"]},
    install_requires=[
        "OpenAIAuth==0.3.2",
        "requests[socks]",
        "httpx[socks]",
        "prompt-toolkit",
        "tiktoken>=0.3.0",
        "openai",
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
    extras_require={
        "WebGPT": ["duckduckgo_search"],
    },
)

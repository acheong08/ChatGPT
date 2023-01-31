from setuptools import find_packages
from setuptools import setup

setup(
    name="revChatGPT",
    version="1.0.2",
    license="GNU General Public License v2.0",
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["revChatGPT", "GPTserver", "Official"],
    url="https://github.com/acheong08/ChatGPT",
    install_requires=[
        "openai",
    ],
    # optional dependencies
    extras_require={
        "api": ["flask"],
        "unofficial": [
            "undetected_chromedriver>=3.1.7",
            "selenium>=4.7.2",
            "tls_client>=0.1.7",
            "2captcha-python>=1.1.3",
        ],
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "revChatGPT = revChatGPT.__main__:main",
            "revApiGPT = revChatGPT.GPTserver:main",
            "OfficialChatGPT = revChatGPT.Official:main",
        ],
    },
)

from setuptools import setup, find_packages
setup(
    name = "revChatGPT",
    version = "0.0.5",
    license = "GNU General Public License v2.0",
    author = "Antonio Cheong",
    author_email = "acheong@student.dalat.org",
    description = "ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    packages = find_packages("src"),
    package_dir={'': 'src'},
    url = "https://github.com/acheong08/ChatGPT",
    install_requires = [
        "requests"
    ],
)

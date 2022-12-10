```
 $ python3 -m revChatGPT --debug

        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        
Type '!help' to show commands
Press enter twice to submit your question.

Logging in...

You:
!help


                !help - Show this message
                !reset - Forget the current conversation
                !refresh - Refresh the session authentication
                !rollback - Rollback the conversation by 1 message
                !config - Show the current configuration
                !exit - Exit the program
```

Refresh every so often in case the token expires.

# Captcha
If you encounter captcha, it saves the image to `captcha.svg` which you can open with your browser. You can then enter the code into the terminal where it asks.
# Setup
`pip3 install --upgrade revChatGPT`

## Dependencies
Run `python3 -m playwright install` after installing `revChatGPT`

## Desktop environments:
A Chrome/Chromium/Firefox window will show up.
1. Wait for the Cloudflare checks to pass
2. Log into OpenAI via the open browser (Google/Email-Password/Etc)
3. It should automatically redirect you to `https://chat.openai.com/chat` after logging in. If it doesn't, go to this link manually after logging in.
4. The window should close automatically
5. You are good to go

## Servers:
You must define the session token in the config:

You can find the session token manually from your browser:
1. Go to `https://chat.openai.com/api/auth/session`
2. Press `F12` to open console
3. Go to `Application` > `Cookies`
4. Copy the session token value in `__Secure-next-auth.session-token`
5. Paste it into `config.json` in the current working directory
```json
{"session_token":"<YOUR_TOKEN>"}
```

You can use `Xvfb` to emulate a desktop environment. It should automatically get the `cf_clearance` given no captcha.

Search it up if you don't know. Ask ChatGPT.


# Config options
```json
{
  "session_token": "<token>",
  "proxy":"<proxy>",
  "accept_language": "en-US,en"
}
```
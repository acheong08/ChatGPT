# Setup

`pip3 install --upgrade revChatGPT`

## Dependencies

Make sure Chrome or Chromium is installed

## Authentication:

You must define the session token or (email and password) for Microsoft Login in the config:

- ### Session Token Authentication:

  You can find the session token manually from your browser:

  1. Go to `https://chat.openai.com/api/auth/session`
  2. Press `F12` to open console
  3. Go to `Application` > `Cookies`
  4. Copy the session token value in `__Secure-next-auth.session-token`
  5. Paste it into `config.json` in the current working directory

  ```json
  { "session_token": "<YOUR_TOKEN>" }
  ```

- ### Microsoft Login Authentication:

  ```json
  { "email": "<EMAIL>", 
    "password":"<PASSWORD>"}
  ```
  Note: `email` and `password` parameters will override `session_token`

You can use `Xvfb` to emulate a desktop environment. It should automatically get the `cf_clearance` given no captcha.

Search it up if you don't know. Ask ChatGPT.

# Config options

```json
{
  "session_token": "<token>",
  "email": "<EMAIL>", 
  "password": "<PASSWORD>",
  "proxy": "<proxy>",
  "verbose": True | False
}
```

# Setup

`pip3 install --upgrade revChatGPT`

(MacOS might need `brew install --cask chromedriver`. View [#380](https://github.com/acheong08/ChatGPT/issues/380))

## Dependencies

Make sure Chrome or Chromium is installed

If you need to select a different version of chrome/chromium, use the `driver_exec_path` and `browser_exec_path` config options

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

- ### Email/Password Login Authentication:

  ```json
  {
    "email": "<EMAIL>",
    "password": "<PASSWORD>",
    "captcha": "<2CAPTCHA_API_KEY>"
  }
  ```

  **Note: 2Captcha is required for Email/Password Login**

- ### Microsoft Login Authentication:

  ```json
  {
    "email": "<EMAIL>",
    "password": "<PASSWORD>",
    "isMicrosoftLogin": True
  }
  ```
```
True → Python dict
true → JSON
```

  **Note: `email` and `password` parameters will override `session_token`**

## Server Config:

You can use `Xvfb` to emulate a a display buffer.

https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1366847803

# Config options (Optional)

```json
{
  "session_token": "<token>",
  "email": "<EMAIL>",
  "password": "<PASSWORD>",
  "captcha": "<2CAPTCHA_API_KEY>",
  "isMicrosoftLogin": True | False,
  "proxy": "<proxy>",
  "driver_exec_path": "./path/to/driver",
  "browser_exec_path": "./path/to/browser",
  "conversation": "<DEFAULT CONVERSATION UUID>",
  "parent_id": "<DEFAULT PARENT ID>"
  "verbose": True | False
}
```
It is impossible to easily get the parent_id and conversation_id from the website. You can only get it programmatically. Don't mess with it unless you know what you are doing

`"driver_exec_path": "/usr/local/bin/chromedriver"` might be necessary for MacOS
```
True → Python dict
true → JSON
```
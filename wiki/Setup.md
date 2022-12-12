# Setup

## Install

`pip3 install revChatGPT --upgrade`

Make the necessary changes in `config.json.example` and save as `config.json` in the current working directory, in `$XDG_CONFIG_HOME/revChatGPT/config.json`, or in `$HOME/revChatGPT/config.json`.

## Session Token Authentication

Currently the only one functional

</summary>

Go to https://chat.openai.com/chat and log in or sign up

1. Open console with `F12`
2. Open `Application` tab > Cookies
![image](https://user-images.githubusercontent.com/36258159/207024908-4c2805cc-2741-4732-86b1-e2e8c19bd23f.png)
3. Copy the value for `__Secure-next-auth.session-token` and paste it into `config.json.example` under `session_token`. 
4. Save the modified file as `config.json` in the current working directory, as `$XDG_CONFIG_HOME/revChatGPT/config.json`, or as `$HOME/revChatGPT/config.json`.

```json
{
  "session_token": "<YOUR_TOKEN>",
  #"proxy": "<HTTP/HTTPS_PROXY>"
}
```

Do not put email/password as that overrides tokens

</details>

<details>
<summary>

## Access Token Authentication

Use this only if all else fails. Refreshing the session does not work here. You have to refresh manually.

</summary>

1. Log in to https://chat.openai.com/
2. Go to https://chat.openai.com/api/auth/session
3. Copy the `accessToken`
4. Replace the <accessToken> with the accessToken value using the below format

```json
{
  "Authorization": "<accessToken>"
}
```

5. Save as `config.json` in the current working directory, as `$XDG_CONFIG_HOME/revChatGPT/config.json`, or as `$HOME/revChatGPT/config.json`.

</details>

<details>
<summary>

## Email and password authentication

</summary>

```json
{
  "email": "<YOUR_EMAIL>",
  "password": "<YOUR_PASSWORD>"
}
```

Save this in `config.json` in current working directory, in `$XDG_CONFIG_HOME/revChatGPT/config.json`, or in `$HOME/revChatGPT/config.json`.

</details>


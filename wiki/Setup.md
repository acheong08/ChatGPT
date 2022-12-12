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
![image](https://user-images.githubusercontent.com/36258159/206955081-8a8e1ff9-d12c-456c-9a67-5c1a7438f76c.png)
3. Copy the value for `__Secure-next-auth.session-token` and paste it into `config.json.example` under `session_token`. 
4. Find your `cf_clearance` cookie and paste it under "cf_clearance"
5. Get your `user-agent` and paste it under "user_agent"
![image](https://user-images.githubusercontent.com/36258159/206944853-3a99fb3b-1081-4a8a-87ea-ab6cadb5a1c4.png)
6. Save the modified file as `config.json` in the current working directory, as `$XDG_CONFIG_HOME/revChatGPT/config.json`, or as `$HOME/revChatGPT/config.json`.

```json
{
  "session_token": "<YOUR_TOKEN>",
  "cf_clearance": "<CLOUDFLARE_TOKEN>",
  "user_agent": "<USER_AGENT>"
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

<details>
<summary>

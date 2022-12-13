# Setup

## Install

`pip3 install revChatGPT==0.0.a42`

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

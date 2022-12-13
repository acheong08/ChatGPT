# Setup

## Install

### On desktop environments: `pip3 install revChatGPT==0.0.42.1`
You also need Google Chrome installed

### On servers: `pip3 install revChatGPT==0.0.38.8`
The server and client must use the same IP address. Use your server as a self-hosted VPN if necessary.

## Basic configuration:
```json
{
  "session_token": "<YOUR_TOKEN>",
  #"cf_clearance": "<CLOUDFLARE_TOKEN>",
  #"user_agent": "<USER_AGENT>",
  #"proxy": "<HTTP/HTTPS_PROXY>"
}
```

## Getting the details
**Note: Do not enter cf_clearance and user_agent on `0.0.a42`. It is for server only `0.0.38.8`**

https://chat.openai.com/chat and getting the correct information: Press `F12`

<details>
<summary>
Guide for getting `session_token`
</summary>

- Find the `__Secure-next-auth.session-token` cookie and copy the value into the config
![image](https://user-images.githubusercontent.com/36258159/207075245-279d8c50-9169-459e-b2b2-9c81b3d05028.png)
</details>

<details>
<summary>
Guide for getting `cf_clearance`
</summary>

![image](https://user-images.githubusercontent.com/36258159/207074293-30f8dac2-be5c-4762-b296-0001799a518b.png)
</details>

<details>
<summary>
Guide for getting `user_agent`
</summary>

![image](https://user-images.githubusercontent.com/36258159/207074671-35ec2970-2bee-4bbb-a22a-7dc690ad1a41.png)
</details>

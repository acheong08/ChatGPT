# Methods of authentication

You cannot put multiple forms of authentication into a config at the same time

## Email/Password

- Does not support Google and Microsoft login
- Uses https://github.com/acheong08/OpenAIAuth to authenticate locally
- Allows you to fetch a `session_token`

## Session token

- This comes from the `__Secure-next-auth.session-token` cookie found on `chat.openai.com`
- It allows you to get a `access_token` via `https://chat.openai.com/api/auth/session`
- This is supported for all account types
- Validity time is unknown

## Access token

- This is what is actually used for authentication and can be found at `https://chat.openai.com/api/auth/session`
- It is valid for 2 weeks
- Recommended method of authentication
- Can be found if you log in to `https://chat.openai.com/` and then go to `https://chat.openai.com/api/auth/session`

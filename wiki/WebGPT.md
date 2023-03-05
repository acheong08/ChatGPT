<a id="revChatGPT.WebGPT"></a>

# revChatGPT.WebGPT

A wrapper for V1 chatbots (both default and async), implementing WebChatGPT browser extension (https://github.com/qunash/chatgpt-advanced/) for revChatGPT
Made by @NymdaFromSalad, per @LuckyHead11 's request and idea

For V3 implementation, see V3 api wiki page

<a id="revChatGPT.WebGPT.Chatbot"></a>

## Chatbot Objects

```python
class WebChatbot(V1.Chatbot)
class WebAsyncChatbot(V1.AsyncChatbot)
```

All functions are inherited (and therefore identical) from respective V1 Chatbots

### Endemic functions

#### webAsk

```python
def webAsk(
        self, prompt, conversation_id=None, parent_id=None, timeout=360, #default Ask parameters
        query=None, numResults=3, timePeriod: str='', region: str='', reply_in: str = 'undefined' #Webify parameters
    ): -> tuple
```

Base function for Web access. Modifies prompt to include search results.

Returns tuple, consisting of \[0\] - Ask() return data, and \[1\] - list of tuples, containing link-title pairs, used for displaying the answer

Additional parameters:
query - optional, search query to display results for. Defaults to prompt
numResults - number of results. I recommend 3 to 10
timePeriod - timeframe for results, accepts following values:
d, w, m and y for last day, week, month and year respectively
region - region to search results for. Uses us-en, ru-ru, ua-uk format. Defaults to wt-wt (no region)
reply_in - will be inserted at the end of the message as reply in {reply_in}. Useful to select the language of the output. By this point i already am not sure, why exactly i put default as 'undefined', but it just works*.

<a id="revChatGPT.WebGPT.Chatbot.webAsk"></a>

#### webAskPlaintext

```python
def webAskPlaintext(
        self, prompt, conversation_id=None, parent_id=None, timeout=360, #default Ask parameters
        query=None, numResults=3, timePeriod: str='', region: str='', reply_in: str = 'undefined' #Webify parameters
    ): -> dict
```

Similar to webAsk, but appends a (human-readable) list of references to the end of the message (yes, even while the answer is not complete)

Returns ask-like result, however the 'message' field is edited

<a id="revChatGPT.WebGPT.Chatbot.webAsk"></a>

#### webAskPlaintext

```python
def webAskMarkdown(
        self, prompt, conversation_id=None, parent_id=None, timeout=360, #default Ask parameters
        query=None, numResults=3, timePeriod: str='', region: str='', reply_in: str = 'undefined' #Webify parameters
    ): -> dict
```

Similar to webAskPlaintext, but instead modifies references to be Text\[number\]\(url\) for use in markdown-enabled outputs

Returns ask-like result, however the 'message' field is edited

<a id="revChatGPT.WebGPT.Chatbot.webAsk"></a>

#### webAskPlaintext

```python
def webify(text:str, query: str, numResults: int, timePeriod: str='', region: str='', reply_in: str='undefined'): -> tuple
```

Returns edited \[prompt\], putting \[numResults\] search results for \[query\] and the instruction for ChatGPT around it.
For additional parameters, look at webAsk description

<a id="revChatGPT.WebGPT.Chatbot.webAsk"></a>

#### BeatifyPlaintext and BeatifyMarkdown

```python
def beatifyPlaintext(response: str, headers: list): -> str
def beatifyMarkdown(response: str, headers: list): -> str
```

Puts references from \[headers\] into \[response\]. Described in webAskPlaintext and webAskMarkdown

<a id="revChatGPT.WebGPT.Chatbot.webAsk"></a>

## Other

Example program for the module:

```Python
from revChatGPT.WebGPT import WebChatbot

chatbot = WebChatbot(config={
  "email": "<emial>",
  "password": "<sapswrod>"
})

#ch_vars = vars(chatbot)

while True:
    prompt = input(">")
    print('thinking')
    for data in chatbot.webAskPlaintext(prompt):
        pass
    print(data["message"])
```

\*Note: 'It Just Works (tm)' is a registered trademark of Bethesda Softworks

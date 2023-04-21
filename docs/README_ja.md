# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

[English](./README.md) - [中文](./README_zh.md) - [Spanish](./README_sp.md) -  日本語

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Support_Platform](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Downloads](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

OpenAI による ChatGPT API をリバースエンジニアリング。チャットボットなどにも拡張可能。

[![](https://github.com/acheong08/ChatGPT/blob/main/docs/view.gif?raw=true)](https://pypi.python.org/pypi/revChatGPT)

> ## 私の仕事を応援してください
>
> プルリクエストを作成し、私の悪いコードを修正してください。
>
> [![support](https://ko-fi.com/img/githubbutton_sm.svg)](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

> #### Discord サーバー: https://discord.gg/9K2BvbXEHT

# インストール

```
python -m pip install --upgrade revChatGPT
```

### サポート Python バージョン

- 最小 - Python3.9
- 推奨 - Python3.11+

<details>

  <summary>

# V1 スタンダード ChatGPT

OpenAI のセキュリティ強化のため、デフォルトのエンドポイントは @pengzhile が提供するものに変更になりました。これはオープンソースではなく、プライバシーは保証されていません。自己責任で使ってください。私は、最新の変更を加えたオープンソースの実装に取り組んでいますが、しばらく時間がかかるかもしれません。

</summary>

## レート制限
- プロキシサーバー: 5 リクエスト / 10 秒
- OpenAI: アカウントごとに 50 リクエスト/時間

## 構成

1. [OpenAI の ChatGPT](https://chat.openai.com/) でアカウントを作成
2. メールアドレスとパスワードを保存

### 認証方法: (1つを選択)

#### - メールアドレス/パスワード

> _現在、無料ユーザーでは壊れています。プラスアカウントをお持ちの方は、`export PUID="..."` を実行してください。PUID は `_puid` という名前のクッキーです_
> Google/Microsoft のアカウントには対応していません。
```json
{
  "email": "email",
  "password": "your password"
}
```

#### - アクセストークン

> これでお願いします！
https://chat.openai.com/api/auth/session

```json
{
  "access_token": "<access_token>"
}
```

#### - オプションの構成:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
  "paid": false,
  "collect_analytics": true,
  "model": "gpt-4"
}
```

Analytics はデフォルトで無効になっています。有効にするには `collect_analytics` を `true` に設定します。

3. これを `$HOME/.config/revChatGPT/config.json` として保存します
4. Windows を使用している場合、スクリプトが config.json ファイルを見つけることができるように、`HOME` という環境変数を作成し、あなたのホームプロファイルに設定する必要があります。

## 使用法

### コマンドライン

`python3 -m revChatGPT.V1`

```
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
Type '!help' to show a full list of commands
Logging in...
You:
(Press Esc followed by Enter to finish)
```

コマンドラインインターフェイスは、複数行の入力をサポートし、矢印キーによるナビゲーションが可能です。また、プロンプトが空の場合、矢印キーで履歴入力を編集することができます。また、前のプロンプトと一致するものがあれば、入力を完了させることができます。入力を終了するには、`Esc` を押してから `Enter` を押します。`Enter` 自体は、複数行モードでは新しい行を作るために使われます。

環境変数 `NO_COLOR` に `true` を設定すると、カラー出力を無効にすることができます。

### 開発者 API

#### 基本的な例 (ストリーミング):

```python
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": "<your access_token>"
})
print("Chatbot: ")
prev_text = ""
for data in chatbot.ask(
    "Hello world",
):
    message = data["message"][len(prev_text) :]
    print(message, end="", flush=True)
    prev_text = data["message"]
print()
```

#### 基本的な例 (単一の結果):

```python
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": "<your access_token>"
})
prompt = "how many beaches does portugal have?"
response = ""
for data in chatbot.ask(
  prompt
):
    response = data["message"]
print(response)
```

#### すべての API メソッド

高度な開発者の使い方については、[wiki](https://github.com/acheong08/ChatGPT/wiki/) を参照してください。

</details>

<summary>

# V3 公式 Chat API

> OpenAI によって最近リリース
>
> - 有料

</summary>

https://platform.openai.com/account/api-keys から API キーを取得する

## コマンドライン

`python3 -m revChatGPT.V3 --api_key <api_key>`

```
  $ python3 -m revChatGPT.V3 --help

    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT

Type '!help' to show a full list of commands
Press Esc followed by Enter or Alt+Enter to send a message.

usage: V3.py [-h] --api_key API_KEY [--temperature TEMPERATURE] [--no_stream] [--base_prompt BASE_PROMPT]
             [--proxy PROXY] [--top_p TOP_P] [--reply_count REPLY_COUNT] [--enable_internet]
             [--config CONFIG] [--submit_key SUBMIT_KEY] [--model {gpt-3.5-turbo,gpt-4,gpt-4-32k}]
             [--truncate_limit TRUNCATE_LIMIT]

options:
  -h, --help            show this help message and exit
  --api_key API_KEY     OpenAI API key
  --temperature TEMPERATURE
                        Temperature for response
  --no_stream           Disable streaming
  --base_prompt BASE_PROMPT
                        Base prompt for chatbot
  --proxy PROXY         Proxy address
  --top_p TOP_P         Top p for response
  --reply_count REPLY_COUNT
                        Number of replies for each prompt
  --enable_internet     Allow ChatGPT to search the internet
  --config CONFIG       Path to V3 config json file
  --submit_key SUBMIT_KEY
                        Custom submit key for chatbot. For more information on keys, see README
  --model {gpt-3.5-turbo,gpt-4,gpt-4-32k}
  --truncate_limit TRUNCATE_LIMIT
```

## 開発者 API

### 基本的な例

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
chatbot.ask("Hello world")
```

### ストリーミングの例

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
for data in chatbot.ask_stream("Hello world"):
    print(data, end="", flush=True)
```

</details>

# Awesome ChatGPT

[私のリスト](https://github.com/stars/acheong08/lists/awesome-chatgpt)

リストに追加してほしいクールなプロジェクトがある場合は、issue を開いてください。

# 免責事項

本製品は OpenAI の公式製品ではありません。これは個人的なプロジェクトであり、OpenAI とは一切関係がありません。私を訴えないでください。

## コントリビューター

このプロジェクトが存在するのは、コントリビュートしてくださるすべての方々のおかげです。

<a href="https://github.com/acheong08/ChatGPT/graphs/contributors">
<img src="https://contrib.rocks/image?repo=acheong08/ChatGPT" />
</a>

## 追加クレジット

- [virtualharby](https://www.youtube.com/@virtualharby) の[この素晴らしい歌](https://www.youtube.com/watch?v=VaMR_xDhsGg)を聴きながらコーディングする

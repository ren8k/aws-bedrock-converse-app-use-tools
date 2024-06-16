# Converse API Deep Dive

本ドキュメントでは，Converse API でツールを利用する際の注意点について解説する．特に，Claude 3 のモデル毎のツールの利用傾向やプロンプトによるツール利用の制御方法，Claude3 Opus のレスポンスに含まれる CoT の内容，ツール実行時の引数生成の失敗ケースなど，Tool use を利用する上で知っておくべき留意点を幅広く取り上げる．また，Converse API がサポートするモデルの一部の引数には制限がある点についても説明する．

### モデルが不必要にツールを利用してしまう課題

Tool use 利用時，モデルが不必要にツールを利用してしまうことがある．例えば，モデルの知識で十分回答できる質問に対しても，Web 検索ツールを利用して回答してしまう．個人的な印象としては，Claude3 Haiku や Opus はツールを利用することが非常に多く，プロンプトでの制御も難しい．一方，Claude3 Sonnet もツールを利用する傾向が強いが，プロンプトでの制御がある程度効きやすい．

> [!TIP] > [Anthropic 公式の Tool use の学習コンテンツ](https://github.com/anthropics/courses/blob/master/ToolUse/04_complete_workflow.ipynb)においても，プロンプトエンジニアリング時に，Claude3 Sonnet を利用している．

以下に，各モデルにおけるツールの利用傾向を示す．（下記は個人環境での実験結果に基づく主観的な印象である点に注意されたい．）

| モデル         | ツールの利用傾向                                         |
| -------------- | -------------------------------------------------------- |
| Claude3 Haiku  | 問答無用でツールを利用                                   |
| Claude3 Sonnet | ツールを積極的に利用する傾向が強いがプロンプトで制御可能 |
| Claude3 Opus   | CoT の過程でどのツールを利用すべきかを思考して利用       |

Anthropic の公式ドキュメント[^6-1]やコード[^6-2]を参考に，下記のようなシステムプロンプトを作成することで，Claude3 Sonnet ではツールの利用を抑制することができた．下記プロンプトの特徴としては，「必要な場合のみツールを利用する」ように指示している点である．

```
あなたは日本人のAIアシスタントです。必ず日本語で回答する必要があります。
以下の<rule>タグ内には厳守すべきルールが記載されています。以下のルールを絶対に守り、ツールを不必要に使用しないで下さい。
<rule>
あなたはツールにアクセスできますが、必要な場合にのみそれらを使用してください。
自身の知識で回答できない場合のみ、関連するツールを使用してユーザーの要求に答えてください。
</rule>

まず、提供されたツールのうち、ユーザーの要求に答えるのに関連するツールはどれかを考えてください。次に、関連するツールの必須パラメータを1つずつ確認し、ユーザーが直接提供したか、値を推測するのに十分な情報を与えているかを判断します。

パラメータを推測できるかどうかを決める際は、特定の値をサポートするかどうかを慎重に検討してください。ただし、必須パラメータの値の1つが欠落している場合は、関数を呼び出さず(欠落しているパラメータに値を入れても呼び出さない)、代わりにユーザーに欠落しているパラメータの提供を求めてください。提供されていないオプションのパラメータについては、追加情報を求めないでください。
```

上記のシステムプロンプトを利用した場合の応答例を以下に示す．下記では，富士山に関する質問は自身の知識で回答しており，Amazon Bedrock に関する質問には知識が無いため，Web 検索ツールを利用して回答している．

<img src="./sonnet_use_tools.png" width="600">

レスポンスの速度や，ツールの利用状況を考慮すると，Claude3 Sonnet は有力なモデルの選択肢であると考えられる．

> [!NOTE]
> Claude3 Sonnet の場合，上記のようなシステムプロンプトでうまく制御できたが，Mistral AI Large の場合は，ツールの利用傾向が低くなるように観察された．モデルの特性を踏まえ，モデル毎に適切なシステムプロンプトを設計することが重要である．

### Tool use で Claude3 Opus を利用したの場合のレスポンスについて

Tool use の設定を行った上で，Claude3 Opus で Converse API を利用すると，レスポンスに必ず CoT の内容が含まれる．具体的には，Converse API で引数`toolConfig`を指定すると，以下のように，`<thinking>`タグ内でどの tools を利用すべきかを思考する．本現象は仕様なのかは不明であるが，もし仕様であれば，CoT の内容は出力しないように工夫すると良いかもしれない．

<img src="./opus_cot.png" width="600">

#### 具体的な実装例（ConverseStream API の場合）

ストリーミング処理で，CoT の内容を含まずに LLM の回答を出力する場合，`src/app/components/chat_interface_streaming.py`の`parse_stream`メソッドを以下のように修正するアイデアがある．具体的には，`<a>`タグで囲まれた LLM の回答のみを表示し，`<thinking>`タグ内の CoT の内容を表示しないようにするようにしている．

```py
def __init__(self, bedrock, cfg):
    self.bedrock = bedrock
    self.cfg = cfg
    self.tool_use_args = {
        "input": {},
        "name": "",
        "toolUseId": "",
    }
    self.tool_use_mode = False
    self.message_cache = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def run(self):
    st.title("Bedrock ConverseStream API Chatbot")

    self.display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        self.display_msg_content(input_msg)
        self.update_chat_history(input_msg)

        response = self.bedrock.generate_response(
            st.session_state.messages, self.cfg
        )
        generated_text: str = self.display_streaming_msg_content(response["stream"])

        # check tool use
        if self.tool_use_mode:
            output_msg = self.create_tool_request_msg(
                generated_text, self.tool_use_args
            )
            self.update_chat_history(output_msg)
            self.tool_use_mode = False

            tool_result_msg = self.execute_tool()
            self.update_chat_history(tool_result_msg)

            response = self.bedrock.generate_response(
                st.session_state.messages, self.cfg
            )
            generated_text = self.display_streaming_msg_content(response["stream"])

        output_msg = {"role": "assistant", "content": [{"text": generated_text}]}
        self.update_chat_history(output_msg)
        # self.print_history(st.session_state.messages)

def chache_msg(self, delta):
    # if message of llm does note include <a> tag, cache the message
    self.message_cache += delta["text"]

def parse_stream(self, response_stream):
    #  extract the LLM's output and tool's input from the streaming response.
    tool_use_input = ""
    self.message_cache = ""
    answer_mode = False
    for event in response_stream:
        print(event)
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                self.chache_msg(delta)
                if "<a>" in delta["text"]:
                    answer_mode = True
                elif "</a>" in delta["text"]:
                    answer_mode = False
                elif answer_mode:
                    yield delta["text"]
            if "toolUse" in delta:
                tool_use_input += delta["toolUse"]["input"]
        if "contentBlockStart" in event:
            self.tool_use_args.update(
                event["contentBlockStart"]["start"]["toolUse"]
            )

        if (
            "messageStop" in event
            and event["messageStop"]["stopReason"] == "tool_use"
        ):
            self.tool_use_args["input"] = json.loads(tool_use_input)
            self.tool_use_mode = True

def stream_message(self, message):
    for word in message.split():
        yield word + " "

def display_streaming_msg_content(self, response_stream):
    if response_stream:
        with st.chat_message("assistant"):
            generated_text = st.write_stream(self.parse_stream(response_stream))
            if not generated_text:
                if self.tool_use_mode:
                    message = "Using Tools..."
                else:
                    message = self.message_cache
                generated_text = st.write_stream(self.stream_message(message))
    return generated_text
```

また，上記のように修正する場合，システムプロンプトは以下のように修正し，LLM の最終的な回答を<a>タグで囲むように指示する必要がある．

```
あなたは日本人のAIアシスタントです。必ず日本語で回答する必要があります。
以下の<rule>タグ内には厳守すべきルールが記載されています。以下のルールを絶対に守り、ツールを不必要に使用しないで下さい。
<rule>
- あなたはツールにアクセスできますが、必要な場合にのみそれらを使用してください。
- 自身の知識で回答できない場合のみ、関連するツールを使用してユーザーの要求に答えてください。
- 必ず回答は<a>タグで囲みなさい。
</rule>

ツールを呼び出す前に、<thinking>タグ内で分析を行ってください。まず、提供されたツールのうち、ユーザーの要求に答えるのに関連するツールはどれかを考えてください。次に、関連するツールの必須パラメータを1つずつ確認し、ユーザーが直接提供したか、値を推測するのに十分な情報を与えているかを判断します。

パラメータを推測できるかどうかを決める際は、特定の値をサポートするかどうかを慎重に検討してください。必須パラメータの値がすべて存在するか、合理的に推測できる場合は、<thinking>タグを閉じてツールの呼び出しに進みます。ただし、必須パラメータの値の1つが欠落している場合は、関数を呼び出さず(欠落しているパラメータに値を入れても呼び出さない)、代わりにユーザーに欠落しているパラメータの提供を求めてください。提供されていないオプションのパラメータについては、追加情報を求めないでください。

以下の形式で回答を出力する必要があります。<a>タグを利用し、フォーマットに注意して、正確に従ってください。
<thinking>分析内容</thinking>
<a>ユーザーの質問に対する回答内容</a>
```

#### 具体的な実装例（Converse API の場合）

Converse API の場合，`src/app/components/chat_interface_standard.py`に`extract_answer`メソッド追加し，`run`メソッド内で利用するアイデアがある．

```py
def extract_answer(self, output_msg, stop_reason=None):
    import re

    if "text" in output_msg["content"][0]:
        text = output_msg["content"][0]["text"]
        print(text)
        pattern = r"<a>(.*?)</a>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            output_msg["content"][0]["text"] = match.group(1)
        elif stop_reason == "tool_use":
            output_msg["content"][0]["text"] = "Using tool..."
    # if text dont include <a> tag, return original output_msg
    return output_msg


def run(self):
    st.title("Bedrock Converse API Chatbot")

    self.display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        self.display_msg_content(input_msg)
        self.update_chat_history(input_msg)

        response = self.bedrock.generate_response(
            st.session_state.messages, self.cfg
        )
        output_msg = response["output"]["message"]
        output_msg = self.extract_answer(output_msg, response["stopReason"])

        # check tool use
        if response["stopReason"] == "tool_use":
            self.display_msg_content(output_msg)
            self.update_chat_history(output_msg)
            tool_use_args = self.get_tool_use_args(output_msg)
            tool_result_msg = self.execute_tool(tool_use_args)
            self.update_chat_history(tool_result_msg)
            response = self.bedrock.generate_response(
                st.session_state.messages, self.cfg
            )
            output_msg = response["output"]["message"]
            output_msg = self.extract_answer(output_msg)

        self.display_msg_content(output_msg)
        self.update_chat_history(output_msg)
        self.print_history(st.session_state.messages)
```

### ツール実行のための引数生成が必ずしも成功するとは限らない

Tool use では，LLM がツールの引数を生成し，ユーザーがツールの実行を行うが，必ずしもツールの引数生成が成功するとは限らない．Claude3 を利用する場合はほぼ失敗はしないが，Command R+ などのモデルを利用する場合，ツールの引数生成に失敗（引数が不足するなど）することが度々ある．

ツールの引数生成失敗に伴うツールの実行失敗を回避するためのリトライの仕組みを実装することが望ましい．（本実装では取り入れていないが，ツールの実行に失敗した場合，エラーの内容を含めて LLM に情報を送信し，それを踏まえて再度引数を生成させることは可能である．[^6-3]）

### 会話履歴にツールの利用履歴がある場合，引数 toolConfig 無しで会話できない

Converse API の引数`messages`に，ツールの利用履歴である`toolUse`や`toolResult`を含む場合，Converse API の引数`toolConfig`を指定する必要がある．例えば，ツールの利用後，会話の途中で引数`toolConfig`を指定せずに Converse API を利用すると，以下のエラーが出る．

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling the Converse operation: The toolConfig field must be defined when using toolUse and toolResult content blocks.
```

本アプリでは，ツールの利用有無をいつでも切り替えることができるが，ツール有り-> ツール無しに切り替える場合，エラーが発生し得る点に注意されたい．

### Claude3 で Tool use 利用時における Converse API のレスポンスの不確定性

Claude3 で Tool use を利用する場合，Converse API，ConverseStream API のレスポンスには，ツールリクエストのための情報（`toolUse`）に加え，生成されたテキスト（`text`）が含まれることがある．

#### Converse API の場合

レスポンス`response["output"]["message"]["content"]`内に`text`が含まれることがある．以下に，Claude3 に「京都府京都市の天気を教えて」と指示した際の Converse API のレスポンス`response["output"]`の例を示す．

```json
{
  "output": {
    "message": {
      "content": [
        { "text": "わかりました。京都府京都市の天気を調べてみましょう。" },
        {
          "toolUse": {
            "input": { "city": "京都市", "prefecture": "京都府" },
            "name": "get_weather",
            "toolUseId": "tooluse_pJ89iJJ4TpywTlztW62UvQ"
          }
        }
      ],
      "role": "assistant"
    }
  }
}
```

上記では，「わかりました。京都府京都市の天気を調べてみましょう。」というテキスト（`text`）に加え，天気予報取得ツールを利用するための情報（`toolUse`）が含まれている．

#### ConverseStream API の場合

ストリーミングのレスポンス`response["stream"]["contentBlockDelta"]["delta"]["text"]`にテキストが含まれることがある．以下に，Claude3 に「京都府京都市の天気を教えて」と指示した際の ConverseStream API のレスポンス`response["stream"]`の例を示す．

```
{'messageStart': {'role': 'assistant'}}
{'contentBlockDelta': {'delta': {'text': 'は'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': 'い'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': '、'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': '分'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': 'か'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': 'り'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': 'ました'}, 'contentBlockIndex': 0}}
{'contentBlockDelta': {'delta': {'text': '。'}, 'contentBlockIndex': 0}}
{'contentBlockStop': {'contentBlockIndex': 0}}
{'contentBlockStart': {'start': {'toolUse': {'toolUseId': 'tooluse_zNriva5iRDaLQj2wy2qkDw', 'name': 'get_weather'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': ''}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '{"pref'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': 'ectu'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': 're": "'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '\\u4eac\\u9'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '0fd\\u5e9c'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '"'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': ', "cit'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': 'y": "\\u4eac'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '\\u90fd'}}, 'contentBlockIndex': 1}}
{'contentBlockDelta': {'delta': {'toolUse': {'input': '"}'}}, 'contentBlockIndex': 1}}
{'contentBlockStop': {'contentBlockIndex': 1}}
{'messageStop': {'stopReason': 'tool_use'}}
{'metadata': {'usage': {'inputTokens': 1219, 'outputTokens': 67, 'totalTokens': 1286}, 'metrics': {'latencyMs': 913}}}
```

上記では，「はい、分かりました。」というテキスト（`text`）に加え，天気予報取得ツールを利用するための情報（`toolUse`）が含まれている．上記を整理すると，以下のような情報を出力している．（上記の`input`内の日本語は，Unicode エスケープシーケンスになっている．）

```json
{
  "content": [
    { "text": "はい、分かりました。" },
    {
      "toolUse": {
        "toolUseId": "tooluse_zNriva5iRDaLQj2wy2qkDw",
        "name": "get_weather",
        "input": { "prefecture": "京都府", "city": "京都市" }
      }
    }
  ],
  "role": "assistant"
}
```

> [!NOTE]
> Converse API, ConverseStream API のレスポンスにテキストが含まれるかは会話内容に依存し不確定であるため，レスポンスの解析には注意が必要である．

### モデル毎の Tool use 利用時における Converse API のレスポンスの差分

Mistral AI Large で Tool use を利用する場合， Converse API におけるレスポンス `response["output"]["message"]`にはテキストは含まれない．以下に Mistral AI Large に「京都府京都市の天気を教えて」と指示した際の Converse API のレスポンス`response["output"]["message"]`を示す．

```json
{
  "content": [
    {
      "toolUse": {
        "input": { "city": "京都市", "prefecture": "京都府" },
        "name": "get_weather",
        "toolUseId": "tooluse_v2wRuKgLRPaQxJJBna0cyw"
      }
    }
  ],
  "role": "assistant"
}
```

一方，Command R+ で Tool use を利用する場合，Converse API におけるレスポンス `response["output"]["message"]`には必ず生成されたテキストが含まれる．以下に，Command R+ に「京都府京都市の天気を教えて」と指示した際の Converse API のレスポンス`response["output"]["message"]`を示す．

```json
{
  "content": [
    { "text": "京都府京都市の天気を検索して、ユーザーに知らせます。" },
    {
      "toolUse": {
        "input": { "city": "京都市", "prefecture": "京都府" },
        "name": "get_weather",
        "toolUseId": "tooluse_WMqogtHhTgOUcjGpRxTrKQ"
      }
    }
  ],
  "role": "assistant"
}
```

### Amazon Titan で Converse API を利用する際の引数`stop sequence`について

Amazon Titan で Converse API を利用する場合，引数`stop sequence`の指定の仕方が他のモデルと異なる．具体的には，引数`stop sequence`には，正規表現パターン「`^(|+|User:)$`」にマッチするような文字列しか指定できない．例えば，Amazon Titan で 引数`stop sequence=["</stop>"]`を指定して Converse API を利用すると以下のエラーが出る．

```
ValidationException: An error occurred (ValidationException) when calling the Converse operation: The model returned the following errors: Malformed input request: string [</stop>] does not match pattern ^(\|+|User:)$, please reformat your input and try again.
```

本アプリでは，Amazon Titan を選択した場合，`stop sequence`のデフォルト値として`User:`を指定するようにしている．

### AI21 Lab で Converse API を利用する際の引数`messages`について

AI21 Labs Jurassic-2 で Converse API を利用する場合，引数`messages`に会話履歴を含めることはできない．例えば，引数`messages`に`assistant`の応答内容を含めると以下のエラーが出る．

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling the Converse operation: This model doesn't support conversation history. Try again with input that only includes one user message.
```

本アプリで AI21 Labs Jurassic-2 を利用する場合，一度会話履歴のキャッシュをクリアしてから利用するように注意されたい．

## References

[^6-1]: [Chain of thought tool use](https://docs.anthropic.com/en/docs/tool-use-examples#chain-of-thought-tool-use)
[^6-2]: [anthropics/courses/ToolUse/02_your_first_simple_tool.ipynb](https://github.com/anthropics/courses/blob/master/ToolUse/02_your_first_simple_tool.ipynb)
[^6-3]: [Use tools with an Amazon Bedrock model](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)

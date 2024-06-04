- streaming は，Claude しか対応してない
- model によっては，stop sequence の指定の仕方が異なるっぽい
  - 折角 Converse API でモデル毎の推論パラメータを気にしなくて良いと謳っているが，，
  - 例えば，Amazon Titan とかで実験すると以下のエラー．

```
ValidationException: An error occurred (ValidationException) when calling the Converse operation: The model returned the following errors: Malformed input request: string [</stop>] does not match pattern ^(\|+|User:)$, please reformat your input and try again.
```

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling the Converse operation: The toolConfig field must be defined when using toolUse and toolResult content blocks.
```

## AWS Documentation

- [Use the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Use tools with an Amazon Bedrock model](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)
- [BedrockRuntime / Client / converse](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html)
- [BedrockRuntime / Client / converse_stream](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse_stream.html)
- [A developer's guide to Bedrock's new Converse API](https://community.aws/content/2dtauBCeDa703x7fDS9Q30MJoBA/amazon-bedrock-converse-api-developer-guide)

## AWS Samples Repository

- [Getting started with the Converse API in Amazon Bedrock](https://github.com/aws-samples/amazon-bedrock-samples/blob/b64902625ea8ade362c0f7d1978428cecdcf47ed/introduction-to-bedrock/Getting%20started%20with%20Converse%20API.ipynb#L158)
- [Function-Calling (Tool Use) with Converse API in Amazon Bedrock](https://github.com/aws-samples/amazon-bedrock-samples/blob/b64902625ea8ade362c0f7d1978428cecdcf47ed/function-calling/Function%20calling%20tool%20use%20with%20Converse%20API.ipynb#L7)
- [advanced-rag-app](https://github.com/aws-samples/aws-ml-jp/blob/main/tasks/generative-ai/advanced-rag/app/app.py)
- [Advanced RAG on AWS 体験ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/9d2259fb-df5f-4f44-b1d3-9a8e0f0f7e46/ja-JP/01-advanced-rag-app/column)
- [aws-samples/streamlit-examples-for-bedrock](https://github.com/aws-samples/streamlit-examples-for-bedrock/blob/main/1-chat.py)

## Qiita

- [Converse API の登場により Bedrock に新モデルが登場したらいち早く試せる画面が完成しました](https://qiita.com/moritalous/items/cde191320abcfffacaca)
- [Amazon Bedrock に Use Tools（Function calling）が来た](https://qiita.com/moritalous/items/8b1a15a7dc583fa3a2e1?utm_campaign=post_article&utm_medium=twitter&utm_source=twitter_share)

## streamlit UI

- [Streamlit の ChatUI 機能を使った簡単な実装例](https://book.st-hakky.com/data-science/streamlit-chat-ui-example/)

## anthropics

- [Tool use (function calling)](https://docs.anthropic.com/ja/docs/tool-use)
- [course/ToolUse](https://github.com/anthropics/courses/tree/master/ToolUse)

## Converse API

- [週刊生成 AI with AWS – 2024/5/27 週](https://aws.amazon.com/jp/blogs/news/weekly-genai-20240527/)

> Amazon Bedrock のメリットのひとつは、統一された Amzaon Bedrock の API で様々な基盤モデルを呼び出せることです。今回、そのメリットを強化する Converse API が公開されました。基盤モデルには、推論時のパラメータをはじめモデル毎に固有の違いがあります。これまで Bedrock を介して基盤モデルを呼び出す場合、モデル毎のパラメータの違いは開発者が考慮し対応する必要がありました。Converse API はこの手間を省き、様々なモデルをシームレスに呼び出すことを可能にします。また、Converse API は複数回の会話のやりとりを行うマルチターン対話や、モデルのツール呼び出し(関数呼び出し)にも対応しています。

---

```json
{
  "toolUse": {
    "input": { "sign": "WZPZ" },
    "name": "top_song",
    "toolUseId": "tooluse_xM0z4SnRS8SCh8VmzsAg_w"
  }
}
```

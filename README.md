# Bedrock（with Converse API + Tool use）を利用したチャットアプリ<!-- omit in toc -->

本リポジトリでは，Amazon Bedrock の Comverse API を利用したチャットアプリを公開している．
本チャットアプリは，以下の機能を持つ．

## TL;DR<!-- omit in toc -->

## 目次<!-- omit in toc -->

- [目的](#目的)
- [オリジナリティ](#オリジナリティ)
- [Converse API とは](#converse-api-とは)
- [function calling とは](#function-calling-とは)
- [前提](#前提)
- [手順](#手順)
- [アプリの機能](#アプリの機能)
  - [リージョン・モデルの切り替え機能](#リージョンモデルの切り替え機能)
  - [推論パラメータの設定機能](#推論パラメータの設定機能)
  - [オプション機能](#オプション機能)
    - [ストリーミング機能の切り替え](#ストリーミング機能の切り替え)
  - [Tools について](#tools-について)
- [コードの説明](#コードの説明)
  - [ディレクトリ構成](#ディレクトリ構成)
  - [コードの解説（streaming）](#コードの解説streaming)
  - [コードの解説（batch）](#コードの解説batch)
  - [注意点](#注意点)
- [References](#references)

## 目的

## オリジナリティ

- ConverseStreamAPI と Use tools を組合せた実装
- Streamlit の ChatUI を利用したチャットアプリ

## Converse API とは

## function calling とは

## 前提

## 手順

<img src="./assets/chat-ui.png" width="800">

## アプリの機能

本アプリの機能として，① リージョン・モデルの切り替え機能，② 推論パラメータの設定機能，③ オプション機能（ストリーミング機能・Use Tools・システムプロンプトの利用選択）がある．以降，各機能について説明する．

<img src="./assets/chat-ui-function.png" width="800">

### リージョン・モデルの切り替え機能

リージョン（`us-west-2` or `us-east-1`）および，Converse API で利用可能なモデルを切り替えることができる．本実装で利用可能なモデルは以下の通りである．

- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`
- `cohere.command-r-plus-v1:0`
- `cohere.command-r-v1:0`
- `mistral.mistral-large-2402-v1:0`
- `mistral.mistral-small-2402-v1:0`
- `meta.llama3-70b-instruct-v1:0`
- `ai21.j2-ultra-v1`
- `ai21.j2-mid-v1`
- `amazon.titan-text-premier-v1:0`
- `amazon.titan-text-lite-v1`

### 推論パラメータの設定機能

Converse API では，引数`inference_config`に対し，以下の推論パラメーターを指定することが可能である．本実装では，以下のパラメーターに加え，System Prompt も設定できるようにしている．

- maxTokens: 生成トークンの最大数
- stopSequences: 停止シーケンスのリスト
- temperature: 温度パラメーター
- topP: 予測トークンの予測確率の累積値

### オプション機能

ストリーミング機能の利用有無，Use Tools の利用有無，システムプロンプトの利用有無を設定可能である．モデルによっては，ストリーミング機能や Tools，システムプロンプトを利用できない[^9]ため，その場合は OFF にして利用することを想定している．以下に，Converse API で利用可能なモデルと，サポートされている機能を整理した表を示す．（執筆時点）

<img src="./assets/supported_model_table.png" width="800" title="キャプションテキスト">

以下に各オプション機能について説明する．

#### ストリーミング機能の切り替え

トグルを ON にすると，`ConverseStream API`が利用され，OFF にすると，`Converse API`が利用される．

### Tools について

## コードの説明

### ディレクトリ構成

### コードの解説（streaming）

### コードの解説（batch）

### 注意点

- モデルの引数の対応について
- 気づいたこととかも共有したい
- 必ずしも function calling が成功するとは限らない
  - command r とかだと，tool 実行に必要な引数をうまく生成できず，ツールの実行に失敗することもある
- 会話履歴に tools の使用履歴が残っている場合，tools 無しの設定で会話できない
  - API の仕様
  - エラーメッセージによると、toolUse と toolResult のコンテンツブロックを使用する場合、toolConfig フィールドを定義する必要があります。つまり、ツールの使用と結果を含むチャットのやり取りを行う際には、そのツールの設定情報を提供しなければならないということです。
- Titan の stop ワードについて笑

## References

[^9]: [Use the Converse API/Supported models and model features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html#conversation-inference-supported-models-features)

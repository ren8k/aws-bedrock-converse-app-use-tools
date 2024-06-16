# Chat App using Bedrock (with Converse API + Tool use)<!-- omit in toc -->

This repository presents a Python implementation of a chat application using Amazon Bedrock's Converse API (Converse [^1-1], ConverseStream [^1-2]), Tool use (function calling) [^1-3], and Streamlit.

> [!NOTE]
> I have posted an article on Qiita explaining this application and the Converse API and Tool use.
> Please check it out!
> <br> [Learn Amazon Bedrock Converse API and Tool use from scratch and implement an advanced chat application](https://qiita.com/ren8k/items/64c4a3de56b886942251)

<img src="./assets/demo.gif">

## Table of Contents<!-- omit in toc -->

- [Objective](#objective)
- [Originality](#originality)
- [Prerequisites](#prerequisites)
- [How to use](#how-to-use)
- [Application Features](#application-features)
  - [1. Region and Model Switching](#1-region-and-model-switching)
  - [2. Inference Parameter Settings](#2-inference-parameter-settings)
  - [3. Optional Features](#3-optional-features)
    - [3-1. Streaming Feature Toggle](#3-1-streaming-feature-toggle)
    - [3-2. Tool Use Toggle](#3-2-tool-use-toggle)
    - [3-3. System Prompt Toggle](#3-3-system-prompt-toggle)
- [Directory Structure and Code Explanation](#directory-structure-and-code-explanation)
- [References](#references)

## Objective

On 2024/05/31, Amazon Bedrock released a new feature called the Converse API. This API provides a unified interface for switching Bedrock models, configuring inference parameters, utilizing external tools (Tool use), and enables streaming processing similar to the existing InvokeModel API. This repository presents a chat application that fully utilizes the features of the Converse API, introduces its functionality, and shares insights.

## Originality

As of the writing date (2024/06/06), there are no chat applications in [aws-samples-repositories](https://github.com/aws-samples) or elsewhere that satisfy the following:

- Implementation combining ConverseStreamAPI and Tool use
- Chat application using Streamlit's ChatUI
- Simplified implementation examples are also provided for reference
  - Stored in src/basic_code

## Prerequisites

In the following regions, Bedrock model access is properly enabled.

- `us-west-2`
- `us-east-1`

## How to use

- Clone this repository

```bash
git clone https://github.com/ren8k/aws-bedrock-converse-app-use-tools.git
cd aws-bedrock-chat-app-with-use-tools
```

- Create and activate a virtual environment (optional)

```bash
python -m venv .venv
source .venv/bin/activate
```

- Install the required libraries

```bash
pip install -r requirements.txt
```

- Run the application

```bash
cd src/app
bash run_app.sh
```

- Launch the application via the URL displayed in the terminal

<img src="./assets/chat-ui.png" width="800">

## Application Features

The features of this application include ① Region and model switching, ② Inference parameter settings, and ③ Optional features (streaming feature, Tool use, and system prompt selection). These features are accessible from the sidebar on the left side of the application.

<img src="./assets/chat-ui-function.png" width="800">

The following sections describe each feature.

### 1. Region and Model Switching

It is possible to switch between regions (`us-west-2` or `us-east-1`) and models available with the Converse API. The models available in this implementation are as follows:

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

### 2. Inference Parameter Settings

With the Converse API, the following inference parameters can be specified for the `inference_config` argument. In addition to these parameters, this implementation also allows setting the System Prompt.

- maxTokens: Maximum number of generated tokens
- stopSequences: List of stop sequences (specified as comma-separated values in the application)
- temperature: Temperature parameter
- topP: Cumulative probability of predicted tokens

### 3. Optional Features

It is possible to enable or disable the streaming feature, Tool use, and the use of system prompts. Some models do not support streaming, Tools, or system prompts [^5-1], so it is expected to turn them OFF when using such models. The table below shows the models available with the Converse API and the supported features. Please note that the table is quoted from the official AWS documentation [^5-1] as of the writing date (2024/06/06).

<img src="./assets/supported_model_table.png" width="800">

> [!IMPORTANT]
> Please note that only Claude3 supports Streaming, and only Claude3, Command R+, and Mistral AI Large support Tool use.

The following sections explain each optional feature.

#### 3-1. Streaming Feature Toggle

When the toggle is ON, the `ConverseStream API` is used, and when OFF, the `Converse API` is used. This feature can be freely switched during a conversation. (The conversation history is carried over.)

#### 3-2. Tool Use Toggle

When the toggle is ON, `Tool use` is enabled. The tool definitions are in [`tools_definition.json`](https://github.com/ren8k/aws-bedrock-chat-app-with-use-tools/blob/main/src/app/tools/tools_definition.json), and the tool implementations are defined in [`tools_func.py`](https://github.com/ren8k/aws-bedrock-chat-app-with-use-tools/blob/main/src/app/tools/tools_func.py).

The tools available in this implementation are as follows. (For simplicity, the implementations within the tools are kept very basic.)

- Weather Forecast Tool: Returns the weather forecast for the specified `prefecture` and `city` arguments
- Web Search Tool: Performs a web search using the specified `search_term` argument and returns the text of the top 3 search results

For reference, the implementations of [`tools_definition.json`](https://github.com/ren8k/aws-bedrock-chat-app-with-use-tools/blob/main/src/app/tools/tools_definition.json) and [`tools_func.py`](https://github.com/ren8k/aws-bedrock-chat-app-with-use-tools/blob/main/src/app/tools/tools_func.py) are shown below. (The tool implementations were based on examples from the official AWS repository.) [^5-2]

<details>
<summary>Tool-related implementations</summary>
<br/>

**tools_definition.json**

```json
[
  {
    "toolSpec": {
      "name": "get_weather",
      "description": "Get weather of a location.",
      "inputSchema": {
        "json": {
          "type": "object",
          "properties": {
            "prefecture": {
              "type": "string",
              "description": "prefecture of the location"
            },
            "city": {
              "type": "string",
              "description": "city of the location"
            }
          },
          "required": ["prefecture", "city"]
        }
      }
    }
  },

  {
    "toolSpec": {
      "name": "web_search",
      "description": "Search a term in the public Internet. Useful for getting up to date information.",
      "inputSchema": {
        "json": {
          "type": "object",
          "properties": {
            "search_term": {
              "type": "string",
              "description": "Term to search in the Internet"
            }
          },
          "required": ["search_term"]
        }
      }
    }
  }
]
```

<br>

**tools_func.py**

```python
import requests
from bs4 import BeautifulSoup
from googlesearch import search


class ToolsList:
    # Define our get_weather tool function...
    def get_weather(self, prefecture, city):
        result = f"Weather in {prefecture}, {city} is 70F and clear skies."
        print(f"Tool result: {result}")
        return result

    # Define our web_search tool function...
    def web_search(self, search_term):
        results = []
        response_list = []
        results.extend([r for r in search(search_term, 3, "en")])
        for j in results:
            response = requests.get(j)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                response_list.append(soup.get_text().strip())
        response_text = ",".join(str(i) for i in response_list)
        # print(f"Search results: {response_text}")
        return response_text

```

</details>
<br/>

#### 3-3. System Prompt Toggle

When the toggle is ON, a system prompt can be specified in the system argument of the `Converse API` and `ConverseStream API`. When OFF, no system prompt is specified.

## Directory Structure and Code Explanation

The implementation of this application is located directly under the `src/app` directory. The directory structure is as follows:

```
.
├── app.py                            : Entry point of the Streamlit application
├── components
│   ├── __init__.py
│   ├── chat_interface_standard.py    : Chat interface using Converse API
│   ├── chat_interface_streaming.py   : Chat interface using ConverseStream API
│   └── sidebar.py                    : UI sidebar
├── config
│   └── config.py                     : Model configuration (inference parameters, tools settings)
├── llm
│   ├── __init__.py
│   └── bedrock_client.py             : Bedrock API client
├── run_app.sh                        : Streamlit application launch script
├── tools
│   ├── __init__.py
│   ├── tools_definition.json         : Tools definition
│   └── tools_func.py                 : Tools implementation (weather forecast, web search)
└── utils
    ├── __init__.py
    └── utils.py                      : Utility functions
```

## References

> [!NOTE]
> We have included notes on using Tool use with the Converse API and advanced topics in [this document](https://github.com/ren8k/aws-bedrock-converse-app-use-tools/blob/main/assets/README.md). Although it overlaps with the content posted on [Qiita](https://qiita.com/ren8k/items/64c4a3de56b886942251), it includes examples of code modifications when using CoT for tool request generation. Please take a look.

[^1-1]: [Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
[^1-2]: [ConverseStream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html)
[^1-3]: [Tool use (function calling)](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)
[^5-1]: [Use the Converse API/Supported models and model features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html#conversation-inference-supported-models-features)
[^5-2]: [Function-Calling（Tool Use） with Converse API in Amazon Bedrock](https://github.com/aws-samples/amazon-bedrock-samples/blob/b64902625ea8ade362c0f7d1978428cecdcf47ed/function-calling/Function%20calling%20tool%20use%20with%20Converse%20API.ipynb)

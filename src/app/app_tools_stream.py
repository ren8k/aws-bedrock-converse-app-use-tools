import json

import boto3
import streamlit as st
from tools.tools_func import ToolsList
from utils.utils import load_json


class CFG:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "あなたは気象予報士です．You have access to tools, but only use them when necessary. If a tool is not required, respond as normal."
    temperature = 0.5
    top_k = 200
    tool_config = {
        "tools": [],
        "toolChoice": {
            "auto": {},
            #'any': {},
            #'tool': {
            #    'name': 'get_weather'
            # }
        },
    }
    tool_config["tools"] = load_json("./tools/tools_definition.json")
    tool_use_args = {
        "input": {},
        "name": "",
        "toolUseId": "",
    }
    tool_use_mode = False


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def generate_streaming_response(messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": CFG.system_prompt}]

    inference_config = {"temperature": CFG.temperature}
    additional_model_fields = {"top_k": CFG.top_k}

    response = bedrock_client.converse_stream(
        modelId=CFG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
        toolConfig=CFG.tool_config,
    )

    return response["stream"]


def display_history(messages):
    for message in messages:
        # exclude use tool result
        if "text" in message["content"][0]:
            display_msg_content(message)


def display_msg_content(message):
    # when request is tool use, sometimes not have text
    if "text" in message["content"][0]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"][0]["text"])


def stream(response_stream):
    # 本関数は，ストリーミングのレスポンスから，LLMの出力およびツールの入力を取得するための関数です．
    tool_use_input = ""
    for event in response_stream:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                yield delta["text"]
            if "toolUse" in delta:
                tool_use_input += delta["toolUse"]["input"]
        if "contentBlockStart" in event:
            CFG.tool_use_args.update(event["contentBlockStart"]["start"]["toolUse"])

        if "messageStop" in event and event["messageStop"]["stopReason"] == "tool_use":
            CFG.tool_use_args["input"] = json.loads(tool_use_input)
            CFG.tool_use_mode = True


def tinking_stream():
    message = "Using Tools..."
    for word in message.split():
        yield word + " "


def display_streaming_msg_content(response_stream):
    if response_stream:
        with st.chat_message("assistant"):
            generated_text = st.write_stream(stream(response_stream))
            if not generated_text:
                generated_text = st.write_stream(tinking_stream)
    return generated_text


def handle_tool_use(function_calling):
    # Get the tool name and arguments:
    tool_name = function_calling["name"]
    tool_args = function_calling["input"] or {}
    # Run the tool:
    print(f"Running ({tool_name}) tool...")
    tool_response = getattr(ToolsList(), tool_name)(**tool_args)
    # Add the tool result to the prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": function_calling["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                }
            ],
        }
    )
    from pprint import pprint

    pprint(st.session_state.messages)
    response_msg = generate_streaming_response(st.session_state.messages)
    generated_text: str = display_streaming_msg_content(response_msg)
    CFG.tool_use_mode = False
    return generated_text


def main():
    st.title("Bedrock Conversation API Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        st.session_state.messages.append(input_msg)

        response_stream = generate_streaming_response(st.session_state.messages)
        generated_text: str = display_streaming_msg_content(response_stream)

        # check tool use
        if CFG.tool_use_mode:
            output_msg = {
                "role": "assistant",
                "content": [{"text": generated_text}, {"toolUse": CFG.tool_use_args}],
            }
            st.session_state.messages.append(output_msg)
            generated_text = handle_tool_use(CFG.tool_use_args)

        output_msg = {"role": "assistant", "content": [{"text": generated_text}]}
        st.session_state.messages.append(output_msg)

    # from pprint import pprint

    # print("#" * 50)
    # pprint(st.session_state.messages)


if __name__ == "__main__":
    main()

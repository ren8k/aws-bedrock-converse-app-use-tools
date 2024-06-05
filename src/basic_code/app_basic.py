import copy
import json

import boto3
import streamlit as st
from tools.tools_func import ToolsList


class CFG:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "You are an AI assistant. You have access to tools, but only use them when necessary. If a tool is not required, respond as normal."
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
    with open("./tools/tools_definition.json", "r") as file:
        tool_config["tools"] = json.load(file)


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def generate_response(messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": CFG.system_prompt}]
    inference_config = {"temperature": CFG.temperature}
    additional_model_fields = {"top_k": CFG.top_k}

    response = bedrock_client.converse(
        modelId=CFG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
        toolConfig=CFG.tool_config,
    )
    return response["output"]["message"], response["stopReason"]


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


def get_tool_use_args(response_msg):
    # sometimes response_msg["content"] include text
    return next((c["toolUse"] for c in response_msg["content"] if "toolUse" in c), None)


def create_tool_result_msg(tool_use_id, tool_response):
    return {
        "role": "user",
        "content": [
            {
                "toolResult": {
                    "toolUseId": tool_use_id,
                    "content": [{"text": tool_response}],
                }
            }
        ],
    }


def run_tool(tool_name, tool_args):
    print(f"Running ({tool_name}) tool...")
    return getattr(ToolsList(), tool_name)(**tool_args)


def execute_tool(tool_use_args):
    tool_name = tool_use_args["name"]
    tool_args = tool_use_args["input"] or {}
    tool_use_id = tool_use_args["toolUseId"]
    print(f"Running ({tool_name}) tool...")
    tool_response = run_tool(tool_name, tool_args)
    tool_result_msg = create_tool_result_msg(tool_use_id, tool_response)
    return tool_result_msg


def update_chat_history(message):
    st.session_state.messages.append(message)


def main():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("Bedrock Conversation API Chatbot")

    display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        update_chat_history(input_msg)

        output_msg, stop_reason = generate_response(st.session_state.messages)
        if stop_reason == "tool_use":
            display_msg_content(output_msg)
            update_chat_history(output_msg)
            tool_use_args = get_tool_use_args(output_msg)
            tool_result_msg = execute_tool(tool_use_args)
            update_chat_history(tool_result_msg)
            output_msg, _ = generate_response(st.session_state.messages)

        display_msg_content(output_msg)
        update_chat_history(output_msg)


if __name__ == "__main__":
    main()

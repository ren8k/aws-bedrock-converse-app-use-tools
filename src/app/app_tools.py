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

    return response["output"]["message"]


def display_history(messages):
    for message in st.session_state.messages:
        # 辞書messageにキーtextが存在する場合
        if "text" in message["content"][0]:
            display_msg_content(message)


def display_msg_content(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"][0]["text"])


def main():
    st.title("Bedrock Conversation API Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        st.session_state.messages.append(input_msg)

        response_msg = generate_response(st.session_state.messages)

        # calling the tool
        function_calling = next(
            (c["toolUse"] for c in response_msg["content"] if "toolUse" in c), None
        )
        if function_calling:
            display_msg_content(response_msg)
            st.session_state.messages.append(response_msg)
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
            response_msg = generate_response(st.session_state.messages)

        display_msg_content(response_msg)
        st.session_state.messages.append(response_msg)

    print("#" * 50)
    print(st.session_state.messages)


if __name__ == "__main__":
    main()

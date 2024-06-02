import copy
import json

import streamlit as st


def chat_interface(bedrock, cfg):
    st.title("Bedrock ConverseStream API Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        append_message(input_msg)

        response_stream = bedrock.generate_streaming_response(st.session_state.messages)
        generated_text: str = display_streaming_msg_content(response_stream, cfg)

        # check tool use
        if cfg.tool_use_mode:
            output_msg = {
                "role": "assistant",
                "content": [{"text": generated_text}, {"toolUse": cfg.tool_use_args}],
            }
            append_message(output_msg)

            tool_result_msg = execute_tool(bedrock, cfg)
            append_message(tool_result_msg)

            response_stream = bedrock.generate_streaming_response(
                st.session_state.messages
            )
            generated_text = display_streaming_msg_content(response_stream, cfg)
            cfg.tool_use_mode = False

        output_msg = {"role": "assistant", "content": [{"text": generated_text}]}
        append_message(output_msg)
        # print_history()


def print_history():
    from pprint import pprint

    print("#" * 50)
    pprint(st.session_state.messages)


def append_message(message):
    st.session_state.messages.append(copy.deepcopy(message))


def display_history(messages):
    for message in messages:
        if "text" in message["content"][0]:
            display_msg_content(message)


def display_msg_content(message):
    if "text" in message["content"][0]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"][0]["text"])


def stream(response_stream, cfg):
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
            cfg.tool_use_args.update(event["contentBlockStart"]["start"]["toolUse"])

        if "messageStop" in event and event["messageStop"]["stopReason"] == "tool_use":
            cfg.tool_use_args["input"] = json.loads(tool_use_input)
            cfg.tool_use_mode = True


def tinking_stream():
    message = "Using Tools..."
    for word in message.split():
        yield word + " "


def display_streaming_msg_content(response_stream, cfg):
    if response_stream:
        with st.chat_message("assistant"):
            generated_text = st.write_stream(stream(response_stream, cfg))
            if not generated_text:
                generated_text = st.write_stream(tinking_stream)
    return generated_text


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


def execute_tool(bedrock, cfg):
    # Get the tool name and arguments:
    tool_name = cfg.tool_use_args["name"]
    tool_args = cfg.tool_use_args["input"] or {}
    tool_use_id = cfg.tool_use_args["toolUseId"]
    print(f"Running ({tool_name}) tool...")
    tool_response = bedrock.run_tool(tool_name, tool_args)
    tool_result_msg = create_tool_result_msg(tool_use_id, tool_response)
    return tool_result_msg

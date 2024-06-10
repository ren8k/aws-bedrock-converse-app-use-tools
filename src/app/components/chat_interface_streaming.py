import copy
import json
from pprint import pprint

import streamlit as st
from tools.tools_func import ToolsList


class ChatInterfaceStreaming:
    def __init__(self, bedrock, cfg):
        self.bedrock = bedrock
        self.cfg = cfg
        self.tool_use_args = {
            "input": {},
            "name": "",
            "toolUseId": "",
        }
        self.tool_use_mode = False
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
            while self.tool_use_mode:
                output_msg = self.create_tool_request_msg(
                    generated_text, self.tool_use_args
                )
                self.update_chat_history(output_msg)

                tool_result_msg = self.execute_tool()
                self.update_chat_history(tool_result_msg)

                response = self.bedrock.generate_response(
                    st.session_state.messages, self.cfg
                )
                generated_text = self.display_streaming_msg_content(response["stream"])

            output_msg = {"role": "assistant", "content": [{"text": generated_text}]}
            self.update_chat_history(output_msg)
            self.print_history(st.session_state.messages)

    def print_history(self, history):
        print("#" * 50)
        pprint(history)

    def update_chat_history(self, message):
        st.session_state.messages.append(copy.deepcopy(message))

    def display_history(self, messages):
        for message in messages:
            if "text" in message["content"][0]:
                self.display_msg_content(message)

    def display_msg_content(self, message):
        if "text" in message["content"][0]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"][0]["text"])

    def parse_stream(self, response_stream):
        #  extract the LLM's output and tool's input from the streaming response.
        tool_use_input = ""
        for event in response_stream:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    yield delta["text"]
                if "toolUse" in delta:
                    tool_use_input += delta["toolUse"]["input"]
            if "contentBlockStart" in event:
                self.tool_use_args.update(
                    event["contentBlockStart"]["start"]["toolUse"]
                )
            if "messageStop" in event:
                stop_reason = event["messageStop"]["stopReason"]
                if stop_reason == "tool_use":
                    self.tool_use_args["input"] = json.loads(tool_use_input)
                    self.tool_use_mode = True
                else:
                    # if stop_reason == 'end_turn'|'max_tokens'|'stop_sequence'|'content_filtered'
                    self.tool_use_mode = False

    def tinking_stream(self):
        message = "Using Tools..."
        for word in message.split():
            yield word + " "

    def display_streaming_msg_content(self, response_stream):
        if response_stream:
            with st.chat_message("assistant"):
                generated_text = st.write_stream(self.parse_stream(response_stream))
                if not generated_text:
                    generated_text = st.write_stream(self.tinking_stream())
        return generated_text

    def create_tool_request_msg(self, generated_text, tool_use_args):
        # tool_use_args includes name, input, and toolUseId
        return {
            "role": "assistant",
            "content": [
                {"text": generated_text},
                {"toolUse": tool_use_args},
            ],
        }

    def create_tool_result_msg(self, tool_use_id, tool_response):
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

    def run_tool(self, tool_name, tool_args):
        return getattr(ToolsList(), tool_name)(**tool_args)

    def execute_tool(self):
        tool_name = self.tool_use_args["name"]
        tool_args = self.tool_use_args["input"] or {}
        tool_use_id = self.tool_use_args["toolUseId"]
        print(f"Running ({tool_name}) tool...")
        tool_response = self.run_tool(tool_name, tool_args)
        tool_result_msg = self.create_tool_result_msg(tool_use_id, tool_response)
        return tool_result_msg

import copy
import json
import re
from pprint import pprint

import streamlit as st
from tools.tools_func import ToolsList


class ChatInterfaceStandard:
    def __init__(self, bedrock, cfg):
        self.bedrock = bedrock
        self.cfg = cfg
        if "messages" not in st.session_state:
            st.session_state.messages = []

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

    def print_history(self, history):
        print("#" * 50)
        pprint(history)

    def update_chat_history(self, message):
        st.session_state.messages.append(copy.deepcopy(message))

    def display_history(self, messages):
        for message in messages:
            # exclude use tool result
            if "text" in message["content"][0]:
                self.display_msg_content(message)

    def extract_answer(self, output_msg, stop_reason=None):
        if "text" in output_msg["content"][0]:
            text = output_msg["content"][0]["text"]
            print(text)
            pattern = r"<a>(.*?)</a>"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                output_msg["content"][0]["text"] = match.group(1)
            elif stop_reason == "tool_use":
                output_msg["content"][0]["text"] = "Using tool..."
        # if text does not include <a> tag, return original output_msg
        return output_msg

    def display_msg_content(self, message):
        # when request is tool use, sometimes not have text
        if "text" in message["content"][0]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"][0]["text"])

    def get_tool_use_args(self, output_msg):
        # sometimes response_msg["content"] include text
        return next(
            (c["toolUse"] for c in output_msg["content"] if "toolUse" in c), None
        )

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

    def execute_tool(self, tool_use_args):
        tool_name = tool_use_args["name"]
        tool_args = tool_use_args["input"] or {}
        tool_use_id = tool_use_args["toolUseId"]
        print(f"Running ({tool_name}) tool...")
        tool_response = self.run_tool(tool_name, tool_args)
        tool_result_msg = self.create_tool_result_msg(tool_use_id, tool_response)
        return tool_result_msg

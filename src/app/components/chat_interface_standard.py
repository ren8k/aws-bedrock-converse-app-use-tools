import copy
import json

import streamlit as st


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

            output_msg, stop_reason = self.bedrock.generate_response(
                st.session_state.messages, self.cfg
            )

            # check tool use
            if stop_reason == "tool_use":
                self.display_msg_content(output_msg)
                self.update_chat_history(output_msg)
                tool_use_args = self.get_tool_use_args(output_msg)
                tool_result_msg = self.execute_tool(tool_use_args)
                self.update_chat_history(tool_result_msg)
                output_msg, _ = self.bedrock.generate_response(
                    st.session_state.messages, self.cfg
                )
            self.display_msg_content(output_msg)
            self.update_chat_history(output_msg)

            self.print_history()

    def print_history(self):
        from pprint import pprint

        print("#" * 50)
        pprint(st.session_state.messages)

    def update_chat_history(self, message):
        st.session_state.messages.append(copy.deepcopy(message))

    def display_history(self, messages):
        for message in messages:
            # exclude use tool result
            if "text" in message["content"][0]:
                self.display_msg_content(message)

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

    def execute_tool(self, tool_use_args):
        tool_name = tool_use_args["name"]
        tool_args = tool_use_args["input"] or {}
        tool_use_id = tool_use_args["toolUseId"]
        print(f"Running ({tool_name}) tool...")
        tool_response = self.bedrock.run_tool(tool_name, tool_args)
        tool_result_msg = self.create_tool_result_msg(tool_use_id, tool_response)
        return tool_result_msg

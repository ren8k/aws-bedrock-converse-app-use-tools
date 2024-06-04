import streamlit as st
from components.chat_interface import ChatInterfaceStreaming
from components.chat_interface_standard import ChatInterfaceStandard
from components.sidebar import sidebar
from config import Config
from llm.bedrock_client import BedrockClient


def main():
    st.set_page_config(page_title="Bedrock Chatbot", layout="wide")

    cfg = Config()
    cfg = sidebar(cfg)
    bedrock_client = BedrockClient(cfg.region)

    if cfg.use_streaming:
        chat_interface = ChatInterfaceStreaming(bedrock_client, cfg)
    else:
        chat_interface = ChatInterfaceStandard(bedrock_client, cfg)
    chat_interface.run()


if __name__ == "__main__":
    main()

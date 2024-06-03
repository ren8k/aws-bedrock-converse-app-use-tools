import streamlit as st
from components.chat_interface import ChatInterface
from components.sidebar import sidebar
from config import Config
from llm.bedrock_client import BedrockClient


def main():
    st.set_page_config(page_title="Bedrock Chatbot", layout="wide")

    cfg = Config()
    sidebar(cfg)
    bedrock_client = BedrockClient(cfg.region)
    chat_interface = ChatInterface(bedrock_client, cfg)
    chat_interface.run()


if __name__ == "__main__":
    main()

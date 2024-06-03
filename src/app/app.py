import streamlit as st
from components.chat_interface import chat_interface
from components.sidebar import sidebar
from config import Config
from llm.bedrock_client import BedrockClient


def main():
    st.set_page_config(page_title="Bedrock Chatbot", layout="wide")

    cfg = Config()
    sidebar(cfg)
    bedrock_client = BedrockClient(cfg)
    chat_interface(bedrock_client, cfg)


if __name__ == "__main__":
    main()

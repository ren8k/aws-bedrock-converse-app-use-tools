import boto3
import streamlit as st


def sidebar(cfg):
    with st.sidebar:
        st.sidebar.header("Settings")
        cfg.region = st.selectbox("region", cfg.REGION_LIST)
        cfg.model_id = st.selectbox("model", cfg.MODEL_LIST)

        st.sidebar.header("Inference parameters")
        cfg.max_tokens = st.number_input("Max Tokens", cfg.max_tokens)
        cfg.stop_sequences = st.text_area(
            "Stop Sequences (Separate with commas)", "</stop>"
        )
        cfg.temperature = st.slider("Temperature", 0.0, 1.0, cfg.temperature, 0.1)
        cfg.top_p = st.slider("Top P", 0.0, 1.0, cfg.top_p)
        cfg.system_prompt = st.text_area("System Prompt", cfg.system_prompt)
    return cfg

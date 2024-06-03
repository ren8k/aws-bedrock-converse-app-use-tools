import boto3
import streamlit as st


def sidebar(cfg):
    with st.sidebar:
        st.sidebar.header("Settings")
        cfg.region = st.selectbox("region", cfg.REGION_LIST)
        cfg.model_id = st.selectbox("model", cfg.MODEL_LIST)

        st.sidebar.header("Inference parameters")
        cfg.max_tokens = st.number_input("Max Tokens", 300)
        cfg.stop_sequences = st.text_area("Stop Sequences", "</stop>")
        cfg.temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.2)
        cfg.top_p = st.slider("Top P", 0.0, 1.0, 0.999)
        cfg.system_prompt = st.text_area("System Prompt", cfg.system_prompt)
    return cfg

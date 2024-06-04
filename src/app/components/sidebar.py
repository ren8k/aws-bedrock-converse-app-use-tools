import boto3
import streamlit as st


def sidebar(cfg):
    with st.sidebar:
        st.sidebar.header("Settings")
        cfg.region = st.selectbox("region", cfg.REGION_LIST)
        cfg.model_id = st.selectbox("model", cfg.MODEL_LIST)

        st.sidebar.header("Inference parameters")
        cfg.max_tokens = st.number_input("Max Tokens", value=cfg.max_tokens)
        if "amazon" in cfg.model_id:
            cfg.stop_sequences = "User:"
        cfg.stop_sequences = st.text_area(
            "Stop Sequences (Separate with commas)", cfg.stop_sequences
        )
        cfg.temperature = st.slider("Temperature", 0.0, 1.0, cfg.temperature, 0.1)
        cfg.top_p = st.slider("Top P", 0.0, 1.0, cfg.top_p)
        cfg.system_prompt = st.text_area("System Prompt", cfg.system_prompt)

        st.sidebar.header("Option")
        cfg.use_streaming = st.toggle("Streaming mode", value=cfg.use_streaming)
        cfg.use_tool_use = st.toggle("Use Tools", value=cfg.use_tool_use)
        cfg.use_system_prompt = st.toggle(
            "Use System Prompt", value=cfg.use_system_prompt
        )

    return cfg

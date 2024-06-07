import json

import boto3
import streamlit as st
from botocore.config import Config


@st.cache_resource
def get_bedrock_client(region):
    retry_config = Config(
        region_name=region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    return boto3.client(
        service_name="bedrock-runtime", config=retry_config, region_name=region
    )


class BedrockClient:
    def __init__(self, region):
        self.client = get_bedrock_client(region)

    def generate_response(self, messages, cfg):
        converse_api_args = self.make_converse_api_args(messages, cfg)
        if cfg.use_streaming:
            response = self.client.converse_stream(**converse_api_args)
        else:
            response = self.client.converse(**converse_api_args)
        return response

    def make_converse_api_args(self, messages, cfg):
        system_prompts = [{"text": cfg.system_prompt}]
        stop_sequences = [s.strip() for s in cfg.stop_sequences.split(",")]

        inference_config = {
            "maxTokens": cfg.max_tokens,
            "stopSequences": stop_sequences,
            "temperature": cfg.temperature,
            "topP": cfg.top_p,
        }

        converse_args = {
            "modelId": cfg.model_id,
            "messages": messages,
            "inferenceConfig": inference_config,
        }

        if cfg.use_tool_use:
            converse_args["toolConfig"] = cfg.tool_config
        if cfg.use_system_prompt:
            converse_args["system"] = system_prompts

        return converse_args

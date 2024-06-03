import json

import boto3
import streamlit as st
from tools.tools_func import ToolsList


@st.cache_resource
def get_bedrock_client(region):
    return boto3.client(service_name="bedrock-runtime", region_name=region)


class BedrockClient:
    def __init__(self, region):
        self.client = get_bedrock_client(region)

    def generate_streaming_response(self, messages, cfg):
        system_prompts = [{"text": cfg.system_prompt}]

        inference_config = {
            "maxTokens": cfg.max_tokens,
            "stopSequences": [cfg.stop_sequences],
            "temperature": cfg.temperature,
            "topP": cfg.top_p,
        }
        # additional_model_fields = {"top_k": cfg.top_k}

        response = self.client.converse_stream(
            modelId=cfg.model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            # additionalModelRequestFields=additional_model_fields,
            toolConfig=cfg.tool_config,
        )

        return response["stream"]

    def run_tool(self, tool_name, tool_args):
        print(f"Running ({tool_name}) tool...")
        return getattr(ToolsList(), tool_name)(**tool_args)

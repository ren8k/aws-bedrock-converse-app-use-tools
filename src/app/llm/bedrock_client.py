import json

import boto3
import streamlit as st
from tools.tools_func import ToolsList


@st.cache_resource
def get_bedrock_client(region):
    return boto3.client(service_name="bedrock-runtime", region_name=region)


class BedrockClient:
    def __init__(self, cfg):
        self.client = get_bedrock_client(cfg.region)
        self.cfg = cfg

    def generate_streaming_response(self, messages):
        system_prompts = [{"text": self.cfg.system_prompt}]

        inference_config = {
            "maxTokens": self.cfg.max_tokens,
            "stopSequences": [self.cfg.stop_sequences],
            "temperature": self.cfg.temperature,
            "topP": self.cfg.top_p,
        }
        # additional_model_fields = {"top_k": self.cfg.top_k}

        response = self.client.converse_stream(
            modelId=self.cfg.model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            # additionalModelRequestFields=additional_model_fields,
            toolConfig=self.cfg.tool_config,
        )

        return response["stream"]

    def run_tool(self, tool_name, tool_args):
        print(f"Running ({tool_name}) tool...")
        return getattr(ToolsList(), tool_name)(**tool_args)

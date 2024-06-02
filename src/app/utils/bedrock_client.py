import boto3
import streamlit as st

from app.config import COnfig


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def generate_response(messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": COnfig.system_prompt}]
    inference_config = {"temperature": COnfig.temperature}
    additional_model_fields = {"top_k": COnfig.top_k}

    response = bedrock_client.converse(
        modelId=COnfig.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
        # toolConfig=CFG.tool_config,
    )

    return response["output"]["message"]

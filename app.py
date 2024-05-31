import logging

import boto3
import streamlit as st
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CFG:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "あなたは大量のデータにアクセスできる日本人のエコノミストです。"
    temperature = 0.5
    top_k = 200


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def generate_response(user_input, messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": CFG.system_prompt}]

    # Base inference parameters to use.
    inference_config = {"temperature": CFG.temperature}
    # Additional inference parameters to use.
    additional_model_fields = {"top_k": CFG.top_k}

    # Send the message.
    response = bedrock_client.converse(
        modelId=CFG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
    )

    return response["output"]["message"]


def main():
    st.title("Bedrock Conversation API Chatbot")

    messages = []
    user_input = st.text_input("あなた: ", "")

    if st.button("送信") and user_input:
        messages.append({"role": "user", "content": [{"text": user_input}]})
        assistant_response = generate_response(user_input, messages)
        messages.append(assistant_response)

        st.write("アシスタント: ")
        for content in assistant_response["content"]:
            st.write(content["text"])
        print("#" * 50)
        print(messages)


if __name__ == "__main__":
    main()

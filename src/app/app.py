import boto3
import streamlit as st


class CFG:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "あなたは大量のデータにアクセスできる日本人のエコノミストです。"
    temperature = 0.5
    top_k = 200


@st.cache_resource
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-west-2")


def generate_response(messages):
    bedrock_client = get_bedrock_client()
    system_prompts = [{"text": CFG.system_prompt}]

    inference_config = {"temperature": CFG.temperature}
    additional_model_fields = {"top_k": CFG.top_k}

    response = bedrock_client.converse(
        modelId=CFG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
    )

    return response["output"]["message"]


def display_history(messages):
    for message in st.session_state.messages:
        display_msg_content(message)


def display_msg_content(message):
    with st.chat_message(message["role"]):
        st.write(content["text"] for content in message["content"])


def main():
    st.title("Bedrock Conversation API Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_history(st.session_state.messages)

    if prompt := st.chat_input("What's up?"):
        input_msg = {"role": "user", "content": [{"text": prompt}]}
        display_msg_content(input_msg)
        st.session_state.messages.append(input_msg)

        response_msg = generate_response(st.session_state.messages)
        display_msg_content(response_msg)
        st.session_state.messages.append(response_msg)


if __name__ == "__main__":
    main()

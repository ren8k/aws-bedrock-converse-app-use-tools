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


def generate_response(user_input, messages):
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


def main():
    st.title("Bedrock Conversation API Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            print(message["content"])
            st.write(content["text"] for content in message["content"])

    user_input = st.text_input("あなた: ", "")

    if st.button("送信") and user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append(
            {"role": "user", "content": [{"text": user_input}]}
        )

        response_msg = generate_response(user_input, st.session_state.messages)
        with st.chat_message("assistant"):
            st.write(content["text"] for content in response_msg["content"])
        st.session_state.messages.append(
            {"role": "assistant", "content": response_msg["content"]}
        )

        # st.write("アシスタント: ")
        # for content in response_msg["content"]:
        #     st.write(content["text"])

    # 会話履歴を画面に表示
    print("#" * 50)
    print(st.session_state.messages)


if __name__ == "__main__":
    main()

import logging

import boto3

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CFG:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "あなたは大量のデータにアクセスできる日本人のエコノミストです。"
    temperature = 0.5
    top_k = 200


def main():
    bedrock_client = boto3.client(
        service_name="bedrock-runtime", region_name="us-west-2"
    )

    user_input = "高インフレが国のGDPに与える影響について20文字で書いてください。"

    message = {"role": "user", "content": [{"text": user_input}]}
    messages = [message]
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

    output_message = response["output"]["message"]

    print(f"Role: {output_message['role']}")
    print(f"Text: {output_message['content'][0]['text']}")

    print("#" * 50)
    messages.append(response["output"]["message"])
    messages.append({"role": "user", "content": [{"text": "具体例を教えてください。"}]})
    # Send the message.
    response = bedrock_client.converse(
        modelId=CFG.model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
    )
    output_message = response["output"]["message"]
    print(f"Role: {output_message['role']}")
    for content in output_message["content"]:
        print(f"Text: {content['text']}")


if __name__ == "__main__":
    main()

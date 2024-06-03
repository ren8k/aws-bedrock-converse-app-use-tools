from utils.utils import load_json


class Config:
    # Bedrock settings
    region = "us-west-2"
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    system_prompt = "関連するツールを使用してユーザーの要求に答えてください(利用可能な場合)。まず、提供されたツールのうち、ユーザーの要求に答えるのに関連するツールはどれかを考えてください。次に、関連するツールの必須パラメータを1つずつ確認し、ユーザーが直接提供したか、値を推測するのに十分な情報を与えているかを判断します。パラメータを推測できるかどうかを決める際は、特定の値をサポートするかどうかを慎重に検討してください。ただし、必須パラメータの値の1つが欠落している場合は、関数を呼び出さず(欠落しているパラメータに値を入れても呼び出さない)、代わりにユーザーに欠落しているパラメータの提供を求めてください。提供されていないオプションのパラメータについては、追加情報を求めないでください。"

    # Converse API parameters
    max_tokens = 500
    stop_sequences = "</stop>"
    temperature = 0.5
    top_p = 0.999
    top_k = 200
    # additional_model_fields = {"top_k": top_k}

    # Tool config
    tool_config = {
        "tools": [],
        "toolChoice": {
            "auto": {},
            #'any': {},
            #'tool': {
            #    'name': 'get_weather'
            # }
        },
    }
    tools_definition_path = "./tools/tools_definition.json"
    tool_config["tools"] = load_json(tools_definition_path)

    # Sidebar options
    REGION_LIST = ["us-west-2", "us-east-1"]
    MODEL_LIST = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0",
        # "cohere.command-r-plus-v1:0",
        # "mistral.mixtral-8x7b-instruct-v0:1",
    ]

import json
import urllib.request

# JMAデータの取得
jma_data_url = "https://www.jma.go.jp/bosai/common/const/area.json"
with urllib.request.urlopen(jma_data_url) as response:
    jma_data = json.loads(response.read().decode())


def lambda_handler(event, context):
    agent = event["agent"]
    actionGroup = event["actionGroup"]
    function = event["function"]
    parameters = event.get("parameters", [])
    # 入力された都道府県名の取得
    input_pref_name = parameters[0]["value"]
    # 都道府県名から対応するコードを検索
    pref_code = search_pref_code(input_pref_name, jma_data["offices"])
    if pref_code:
        # 天気予報の取得
        forecast_url = (
            f"https://www.jma.go.jp/bosai/forecast/data/forecast/{pref_code}.json"
        )
        with urllib.request.urlopen(forecast_url) as response:
            forecast_data = json.loads(response.read().decode())
            responseBody = {
                "TEXT": {"body": json.dumps(forecast_data, ensure_ascii=False)}
            }
            action_response = {
                "actionGroup": actionGroup,
                "function": function,
                "functionResponse": {"responseBody": responseBody},
            }
            function_response = {
                "messageVersion": event["messageVersion"],
                "response": action_response,
            }
            print("Response: {}".format(function_response))
            return function_response
    else:
        return "入力された都道府県が見つかりませんでした。"


def search_pref_code(pref_name, offices):
    for code, office in offices.items():
        if office["name"] == pref_name:
            return code
    return None

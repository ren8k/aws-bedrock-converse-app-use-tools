import requests
from bs4 import BeautifulSoup
from googlesearch import search


# https://github.com/aws-samples/amazon-bedrock-samples/blob/b64902625ea8ade362c0f7d1978428cecdcf47ed/function-calling/Function%20calling%20tool%20use%20with%20Converse%20API.ipynb#L7
class ToolsList:
    # Define our get_weather tool function...
    def get_weather(self, prefecture, city):
        result = f"Weather in {prefecture}, {city} is 70F and clear skies."
        print(f"Tool result: {result}")
        return result

    # Define our web_search tool function...
    def web_search(self, search_term):
        results = []
        response_list = []
        results.extend([r for r in search(search_term, 3, "en")])
        for j in results:
            response = requests.get(j)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                response_list.append(soup.get_text().strip())
        response_text = ",".join(str(i) for i in response_list)
        # print(f"Search results: {response_text}")
        return response_text

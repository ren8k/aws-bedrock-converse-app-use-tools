class ToolsList:
    # Define our get_weather tool function...
    def get_weather(self, city, state):
        # print(city, state)
        result = f"Weather in {city}, {state} is 70F and clear skies."
        print(f"Tool result: {result}")
        return result

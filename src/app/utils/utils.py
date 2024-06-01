import json
from typing import Any


def load_json(config_path: str) -> Any:
    with open(config_path, "r") as file:
        return json.load(file)

class OpenaiApiError(Exception):
    def __init__(self, response_json: dict[str, str]) -> None:
        self.message: str = response_json["error"]["message"]
        self.type: str = response_json["error"]["type"]

    def __str__(self) -> str:
        return self.message

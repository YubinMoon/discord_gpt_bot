from .client import Client


class GPTContainer:
    def __init__(self, apk_key: str):
        self.api_key = apk_key
        self.Client_container = {}

    # get gpt by channel id
    def get_gpt(self, key: int, api_key: str | None = None) -> Client:
        if key in self.Client_container:
            return self.Client_container[key]
        else:
            self.Client_container[key] = Client(api_key if api_key else self.api_key)
            return self.Client_container[key]

    def __str__(self) -> str:
        return f"< ClientBox : {self.Client_container.keys()} >"

from .gpt import GPT


class GPTBox:
    def __init__(self, apk_key: str):
        self.api_key = apk_key
        self.gpt_container = {}

    # get gpt by channel id
    def get_gpt(self, channel_id: int, api_key: str | None = None) -> GPT:
        if channel_id in self.gpt_container:
            return self.gpt_container[channel_id]
        else:
            self.gpt_container[channel_id] = GPT(api_key if api_key else self.api_key)
            return self.gpt_container[channel_id]

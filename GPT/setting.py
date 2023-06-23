import os
import json


class Setting:
    def __init__(self):
        self.setting_type = {
            "model": str,
            "system_text": str,
            "max_token": int,
            "temperature": float,
            "top_p": float,
            "keep_min": int,
        }
        self.setting_value = {
            "model": "gpt-3.5-turbo-0613",
            "system_text": "",
            "max_token": 3000,
            "temperature": 1.0,
            "top_p": 1.0,
            "keep_min": 10,
        }
        self.setting_enum = {
            "model": [
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
                "gpt-4",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0613	",
            ]
        }
        self.sync_setting()

    def sync_setting(self) -> None:
        self.model = self.setting_value["model"]
        self.system_text = self.setting_value["system_text"]
        self.max_token = self.setting_value["max_token"]
        self.temperature = self.setting_value["temperature"]
        self.top_p = self.setting_value["top_p"]
        self.keep_min = self.setting_value["keep_min"]

    def set_setting(self, key: str, value: str) -> None:
        if key not in self.setting_value:
            raise KeyError(f"'{key}'이라는 설정은 존재하지 않습니다.")
        if key in self.setting_enum and value not in self.setting_enum[key]:
            raise ValueError(f"'{key}'의 값은 {self.setting_enum[key]} 중 하나여야 합니다.")
        self.setting_value[key] = self.setting_type[key](value)
        self.sync_setting()

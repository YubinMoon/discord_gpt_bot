import os
import json


class Setting:
    def __init__(self, file_name: str = "setting.json"):
        self.file_name = file_name
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
            "max_token": 4000,
            "temperature": 1.0,
            "top_p": 1.0,
            "keep_min": 10,
        }
        self.load_from_json()
        self.sync_setting()

    def load_from_json(self) -> None:
        if os.path.isfile(self.file_name):
            loaded_settings = json.load(open(self.file_name, "r", encoding="utf-8"))
            self.load_from_dict(loaded_settings)

    def load_from_dict(self, settings: dict) -> None:
        for key, value in self.setting_value.items():
            self.setting_value[key] = settings.get(key, value)

    def set_setting(self, key: str, value: str) -> None:
        if key not in self.setting_value:
            raise KeyError(f"'{key}'이라는 설정은 존재하지 않습니다.")
        self.setting_value[key] = self.setting_type[key](value)
        self.save_to_json()
        self.sync_setting()

    def save_to_json(self) -> None:
        json.dump(self.setting_value, open(self.file_name, "w", encoding="utf-8"))

    def sync_setting(self) -> None:
        self.model = self.setting_value["model"]
        self.system_text = self.setting_value["system_text"]
        self.max_token = self.setting_value["max_token"]
        self.temperature = self.setting_value["temperature"]
        self.top_p = self.setting_value["top_p"]
        self.keep_min = self.setting_value["keep_min"]

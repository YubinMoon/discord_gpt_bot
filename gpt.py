import openai
import json
import time
import logging

logger = logging.getLogger(__name__)
requestLogger = logging.getLogger("request")
fileHeader = logging.FileHandler("request.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(message)s")
fileHeader.setFormatter(formatter)
requestLogger.addHandler(fileHeader)
requestLogger.propagate = 0


class GPT:
    def __init__(self):
        self.lastRequestTime = time.time()
        openai.api_key_path= "api_openai"
        try:
            self.userSetting = json.load(open("user_setting.json", "r"))
        except:
            self.userSetting = {}
        try:
            self.gloSetting = json.load(
                open("setting.json", "r", encoding="utf-8"))
        except:
            self.gloSetting = {
                "settings_text": "",
                "history": [],
                "max_token": 1000,
                "disable_system": False,
                "show_question": False
            }
            json.dump(self.gloSetting, open(
                "setting.json", "w", encoding="utf-8"), indent=4)

    def completion(self, new_message_text: str, settings_text: str = '', past_messages: list = []):
        if len(past_messages) == 0 and len(settings_text) != 0:
            system = {"role": "system", "content": settings_text}
            past_messages.append(system)
        new_message = {"role": "user", "content": new_message_text}
        past_messages.append(new_message)

        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=past_messages
        )
        requestLogger.info(
            bytes(str(result), "utf-8").decode("unicode_escape"))

        response_message = {"role": "assistant",
                            "content": result.choices[0].message.content}
        past_messages.append(response_message)
        response_message_text = result.choices[0].message.content
        past_messages = self.controlPastMSG(
            result.usage.total_tokens, past_messages)
        logger.info(past_messages)
        return response_message_text, past_messages

    def controlPastMSG(self, token, past_messages):
        try:
            logger.info(f"token: {token}")
            if (token > self.gloSetting["max_token"]):
                his = past_messages
                past_messages = []
                if his[0]["role"] == "system":
                    past_messages += his[0]
                    past_messages += his[3:]
                else:
                    past_messages += his[2:]
            return past_messages
        except:
            logger.exception("으아ㅏㅏㅏ")

    async def clearHistory(self):
        logger.info("history cleared")
        self.gloSetting["history"] = []

    def gloRequest(self, message):
        if time.time() - self.lastRequestTime > 600:
            self.gloSetting["history"] = []
        his = self.gloSetting["history"]
        setting = self.gloSetting["settings_text"]
        result, his = self.completion(message, setting, his)
        self.gloSetting["history"] = his
        return result

    def setSetting(self, setting):
        self.gloSetting["settings_text"] = setting
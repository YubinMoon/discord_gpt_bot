import openai
import json
import time
import logging
import asyncio
import tiktoken
import os


class GPT:
    def __init__(self):
        self.init_logger()
        self.lastRequestTime = time.time()
        openai.api_key_path = "api_openai"
        if os.path.isfile("setting.json"):
            self.gloSetting = json.load(
                open("setting.json", "r", encoding="utf-8"))
        else:
            self.create_global_settings()

    def init_logger(self):
        self.logger = logging.getLogger(__name__)
        fileHeader = logging.FileHandler("request.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        fileHeader.setFormatter(formatter)

    def create_global_settings(self):
        self.gloSetting = {
            "system_text": "",
            "history": [],
            "max_token": 2000,
            "disable_system": False,
            "show_question": False
        }
        json.dump(self.gloSetting, open(
            "setting.json", "w", encoding="utf-8"), indent=4)

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
    See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def make_new_messages(self, new_message_text: str, system_text: str, past_messages: list):
        system = {"role": "system", "content": system_text}
        new_message = {"role": "user", "content": new_message_text}
        message = [system] + (past_messages or []) + [new_message]
        return message

    def completion(self, new_message_text: str, system_text: str = "", past_messages: list = None):
        past_messages = past_messages or []
        past_messages = self.control_token(past_messages)
        message = self.make_new_messages(
            new_message_text, system_text, past_messages)

        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )
        response = result.choices[0].message.content
        response_message = {"role": "assistant",
                            "content": response}
        past_messages.append(response_message)
        self.logger.info(past_messages)
        return response, past_messages

    def glo_request(self, message):
        if time.time() - self.lastRequestTime > 600:
            self.gloSetting["history"] = []
            self.lastRequestTime = time.time()
        his = self.gloSetting["history"]
        setting = self.gloSetting["system_text"]
        result, his = self.completion(message, setting, his)
        self.gloSetting["history"] = his
        return result

    def control_token(self, past_messages = []):
        try:
            token = self.num_tokens_from_messages(past_messages)
            self.logger.info(f"token: {token}")
            while (token > self.gloSetting.get("max_token", 3000) and past_messages):
                past_messages = past_messages[2:]
                token = self.num_tokens_from_messages(past_messages)
            return past_messages
        except:
            self.logger.exception("Error in controlling past messages")

    async def clear_history(self):
        self.logger.info("history cleared")
        self.gloSetting["history"] = []

    async def stream_completion(self, new_message_text: str, system_text: str = '', past_messages: list = []):
        past_messages = past_messages or []
        messages = self.make_new_messages(
            new_message_text, system_text, past_messages)

        result = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            stream=True,
            messages=messages
        )

        collected_messages = []

        for chunk in result:
            chunk_message = chunk['choices'][0]['delta'].get("content","")
            yield chunk_message
            collected_messages.append(chunk_message)

        full_reply_content = ''.join(
            [m for m in collected_messages])

        past_messages.append({"role": "assistant",
                            "content": full_reply_content})
        past_messages = self.control_token(past_messages)
        self.logger.info(past_messages)
        self.gloSetting["history"] = past_messages
        return

    async def stream_request(self, message):
        if time.time() - self.lastRequestTime > 600:
            self.gloSetting["history"] = []
            self.lastRequestTime = time.time()
        setting = self.gloSetting["system_text"]
        his = self.gloSetting["history"]
        async for result in self.stream_completion(message, setting, his):
            yield result

    def set_system_text(self, setting):
        self.gloSetting["system_text"] = setting

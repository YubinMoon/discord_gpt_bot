import openai.error
import time
import logging
import os
import aiohttp
import traceback
import datetime
import io
from dotenv import load_dotenv
from .setting import Setting
from .chat import stream_chat_request, chat_request
from .message import MessageLine, MessageBox
from .token import Tokener


class GPT:
    def __init__(self, api_key: str, setting_file: str = "setting.json"):
        self.setting = Setting(setting_file)
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.message_box = MessageBox()
        self.lastRequestTime = time.time()
        if not os.path.isdir("./img"):
            os.mkdir("img")
        self.clear_history()

    def control_token(self):
        try:
            token = Tokener.num_tokens_from_messages(self.history)

            self.logger.info(f"use token: {token}")
            # 토큰 수가 최대값을 초과하면, 최근 2개 이전의 메시지를 제거합니다.
            while token > self.setting.max_token and past_messages:
                past_messages = past_messages[2:]
                token = Tokener.num_tokens_from_messages(past_messages)
        except:
            self.logger.exception("Error in controlling past messages")

    def make_messages(
        self, new_message_text: str, system_text: str, _past_messages: list = []
    ) -> list[dict[str, str]]:
        message = []
        if self.setting.system_text:
            message.append(
                self.make_line(role="system", content=self.setting.system_text)
            )
        new_message = self.make_line(content=new_message_text)
        message = message + _past_messages + [new_message]
        return message

    async def get_stream_chat(self, _message: str):
        self.is_timeout()
        self.message_box.add_message(MessageLine(role="user", content=_message))
        messages = self.message_box.make_messages(setting=self.setting)
        self.logger.info(f"message: {messages}")

        collected_messages = MessageLine()
        async for data in self.get_chat_stream_data(messages):
            new_message = MessageLine(data=data)
            collected_messages += new_message
            yield new_message.content

        self.logger.info(f"request: {collected_messages}")
        self.message_box.add_message(collected_messages)

    async def get_chat_stream_data(self, messages: list):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": self.setting.model,
                "messages": messages,
                "temperature": self.setting.temperature,
                "top_p": self.setting.top_p,
                "stream": True,
            }
            async for data in stream_chat_request(headers=headers, data=data):
                yield data

        except aiohttp.ClientConnectionError:
            self.logger.exception(traceback.print_exc())
            yield "API 연결 실패"
        except aiohttp.ClientResponseError:
            self.logger.exception(traceback.print_exc())
            yield "API 응답 오류"
        except Exception as e:
            self.logger.exception(traceback.print_exc())
            yield "API 에러"
            raise openai.error.APIConnectionError("연결 실패") from e

    async def short_chat(self, message: str, system: str | None = None):
        messages: list[MessageLine] = []
        if system:
            messages.append(MessageLine(role="system", content=system))
        messages.append(MessageLine(role="user", content=message))
        messages = [message.make_message() for message in messages]
        self.logger.info(f"message: {messages}")

        result = await self.get_chat_data(messages)

        self.logger.info(f"request: {result}")
        return result

    async def get_chat_data(self, messages: list) -> str:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": self.setting.model,
                "messages": messages,
                "temperature": self.setting.temperature,
                "top_p": self.setting.top_p,
            }
            return await chat_request(headers=headers, data=data)

        except aiohttp.ClientConnectionError:
            self.logger.exception(traceback.print_exc())
            return "API 연결 실패"
        except aiohttp.ClientResponseError:
            self.logger.exception(traceback.print_exc())
            return "API 응답 오류"
        except Exception:
            self.logger.exception(traceback.print_exc())
            return "API 에러"

    async def create_image(self, prompt: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        async with self.session.post(
            "https://api.openai.com/v1/images/generations", headers=headers, json=data
        ) as resp:
            if resp.status != 200:
                print(resp)
                raise Exception("API 요청 에러")
            result = await resp.json()
            url = result["data"][0]["url"]
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with open(
                    f"./img/{datetime.datetime.now().strftime('%m%d%H%M%S')}.png", "wb"
                ) as f:
                    f.write(data)
                image_data = io.BytesIO(data)
                return image_data
            else:
                raise Exception("이미지 다운 에러")

    def clear_history(self):
        self.logger.info("history cleared")
        self.message_box.clear()

    def set_system_text(self, setting):  # TODO 셋팅 변경 추가
        pass
        # self.system_text = setting
        # self.load_setting()

    def is_timeout(self):
        if time.time() - self.lastRequestTime > self.setting.keep_min * 60:
            self.clear_history()
        self.lastRequestTime = time.time()

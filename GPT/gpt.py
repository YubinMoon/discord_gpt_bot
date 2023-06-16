import openai.error
import time
import logging
import os
import aiohttp
import traceback
import datetime
import io
from typing import AsyncIterator
from dotenv import load_dotenv
from .setting import Setting
from .chat import stream_chat_request, Chat, ChatStream
from .message import MessageLine, MessageBox
from .token import Tokener

logger = logging.getLogger(__name__)


class GPT:
    def __init__(self, api_key: str, setting_file: str = "setting.json"):
        self.setting = Setting(setting_file)
        self.api_key = api_key
        self.message_box = MessageBox()
        self.lastRequestTime = time.time()
        if not os.path.isdir("./img"):
            os.mkdir("img")
        self.clear_history()

    async def get_stream_chat(self, _message: str) -> AsyncIterator[MessageLine]:
        self.is_timeout()
        self.message_box.add_message(MessageLine(role="user", content=_message))
        messages = self.message_box.make_messages(setting=self.setting)
        chat_api = ChatStream(api_key=self.api_key)
        logger.info(f"message: {messages}")

        collected_messages = MessageLine()
        # async for data in self.get_chat_stream_data(messages):
        async for data in chat_api.run(messages, setting=self.setting):
            collected_messages = MessageLine(data=data)
            yield collected_messages

        logger.info(f"request: {collected_messages}")
        self.message_box.add_message(collected_messages)

    async def get_chat_stream_with_function(self, messages: list, function: list):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": self.setting.model,
                "messages": messages,
                "functions": function,
                "function_call": "auto",
                "temperature": self.setting.temperature,
                "top_p": self.setting.top_p,
                "stream": True,
            }
            async for data in stream_chat_request(headers=headers, data=data):
                yield data

        except aiohttp.ClientConnectionError:
            logger.exception(traceback.print_exc())
            yield "API 연결 실패"
        except aiohttp.ClientResponseError:
            logger.exception(traceback.print_exc())
            yield "API 응답 오류"
        except Exception as e:
            logger.exception(traceback.print_exc())
            yield "API 에러"
            raise openai.error.APIConnectionError("연결 실패") from e

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
            async for data in ChatStream.run(headers=headers, data=data):
                yield data

        except aiohttp.ClientConnectionError:
            logger.exception(traceback.print_exc())
            yield "API 연결 실패"
        except aiohttp.ClientResponseError:
            logger.exception(traceback.print_exc())
            yield "API 응답 오류"
        except Exception as e:
            logger.exception(traceback.print_exc())
            yield "API 에러"
            raise openai.error.APIConnectionError("연결 실패") from e

    async def short_chat(self, message: str, system: str | None = None) -> str:
        messages: list[MessageLine] = []
        if system:
            messages.append(MessageLine(role="system", content=system))
        messages.append(MessageLine(role="user", content=message))
        messages = [message.make_message() for message in messages]
        chat_api = Chat(api_key=self.api_key)
        logger.info(f"message: {messages}")

        result = await chat_api.run(messages, self.setting)

        logger.info(f"request: {result}")
        return result

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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
            ) as resp:
                if resp.status != 200:
                    logger.error(resp)
                    raise Exception("API 요청 에러")
                result = await resp.json()
                logger.info(result)
                url = result["data"][0]["url"]
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    with open(
                        f"./img/{datetime.datetime.now().strftime('%m%d%H%M%S')}.png",
                        "wb",
                    ) as f:
                        f.write(data)
                    image_data = io.BytesIO(data)
                    return image_data
                else:
                    raise Exception("이미지 다운 에러")

    def clear_history(self):
        logger.info("history cleared")
        self.message_box.clear()

    def is_timeout(self):
        if time.time() - self.lastRequestTime > self.setting.keep_min * 60:
            self.clear_history()
        self.lastRequestTime = time.time()

    def make_dummy_function(self) -> list:
        return [
            {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

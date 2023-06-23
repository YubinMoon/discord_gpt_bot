import time
import logging
import os
import aiohttp
import datetime
import io
from typing import AsyncIterator
from .setting import Setting
from .chat import Chat, ChatStream, ChatStreamFunction
from .message import (
    BaseMessage,
    SystemMessage,
    UserMessage,
    AssistanceMessage,
    FunctionMessage,
    MessageBox,
)
from .container import Container
from .function import FunctionManager, TestFunction, ScheduleFunction

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, container: Container):
        self.container = container
        self.setting = Setting()
        self.message_box = MessageBox()
        self.function_manager = FunctionManager()
        self.lastRequestTime = time.time()
        if not os.path.isdir("./img"):
            os.mkdir("img")
        self.clear_history()
        self.set_function()

    def set_function(self):
        self.function_manager.add_function(TestFunction())
        self.function_manager.add_function(ScheduleFunction())

    async def get_stream_chat(self, _message: str) -> AsyncIterator[AssistanceMessage]:
        self.is_timeout()
        self.message_box.add_message(UserMessage(content=_message))
        messages = self.message_box.make_messages(setting=self.setting)
        chat_api = self.container.get_gpt_chat("stream")
        logger.info(f"message: {messages}")

        collected_messages = AssistanceMessage()
        # async for data in self.get_chat_stream_data(messages):
        async for data in chat_api.run(messages, setting=self.setting):
            collected_messages += AssistanceMessage(data=data)
            yield collected_messages

        logger.info(f"request: {collected_messages}")
        self.message_box.add_message(collected_messages)

    async def get_stream_chat_with_function(self, _message: str) -> AsyncIterator[str]:
        self.is_timeout()
        self.message_box.add_message(UserMessage(content=_message))
        function_data = self.function_manager.make_dict()
        chat_api = self.container.get_gpt_chat("stream_function")
        call_functions = []
        while True:
            collected_messages = AssistanceMessage()
            messages = self.message_box.make_messages(setting=self.setting)
            logger.info(f"message: {messages}")
            async for data in chat_api.run(
                messages, function=function_data, setting=self.setting
            ):
                temp_messages = AssistanceMessage(data=data)
                yield temp_messages.content
                collected_messages += temp_messages
            logger.info(f"request: {collected_messages}")
            self.message_box.add_message(collected_messages)
            if collected_messages.finish_reason != AssistanceMessage.FUNCTION_CALL:
                break
            yield f"call function: {collected_messages.function_call} \n"
            function_message = await self.function_manager.run(collected_messages)
            self.message_box.add_message(function_message)
            collected_messages.content = function_message.name + "\n"

    async def short_chat(self, message: str, system: str | None = None) -> str:
        messages: list[BaseMessage] = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(UserMessage(content=message))
        messages = [message.make_message() for message in messages]
        chat_api = self.container.get_gpt_chat("completion")
        logger.info(f"message: {messages}")

        result = await chat_api.run(messages, self.setting)

        logger.info(f"request: {result}")
        return result

    # TODO image 생성
    # async def create_image(self, prompt: str):
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {self.api_key}",
    #     }
    #     data = {
    #         "prompt": prompt,
    #         "n": 1,
    #         "size": "1024x1024",
    #     }
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(
    #             "https://api.openai.com/v1/images/generations",
    #             headers=headers,
    #             json=data,
    #         ) as resp:
    #             if resp.status != 200:
    #                 logger.error(resp)
    #                 raise Exception("API 요청 에러")
    #             result = await resp.json()
    #             logger.info(result)
    #             url = result["data"][0]["url"]
    #         async with session.get(url) as response:
    #             if response.status == 200:
    #                 data = await response.read()
    #                 with open(
    #                     f"./img/{datetime.datetime.now().strftime('%m%d%H%M%S')}.png",
    #                     "wb",
    #                 ) as f:
    #                     f.write(data)
    #                 image_data = io.BytesIO(data)
    #                 return image_data
    #             else:
    #                 raise Exception("이미지 다운 에러")

    def clear_history(self):
        logger.info("history cleared")
        self.message_box.clear()

    def is_timeout(self):
        if time.time() - self.lastRequestTime > self.setting.keep_min * 60:
            self.clear_history()
        self.lastRequestTime = time.time()

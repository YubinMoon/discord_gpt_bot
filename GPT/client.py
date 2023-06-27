import time
import logging
import os
import aiohttp
import datetime
import io
from typing import AsyncIterator

from GPT.error import OpenaiApiError
from .setting import Setting
from .message import (
    BaseMessage,
    SystemMessage,
    UserMessage,
    AssistanceMessage,
    FunctionMessage,
    MessageBox,
)
from .function import FunctionManager, TestFunction, ScheduleFunction
from .interface import BaseClient, BaseContainer, BaseChat

logger = logging.getLogger(__name__)


class Client(BaseClient):
    def __init__(self, container: BaseContainer):
        super().__init__(container)
        self.setting = Setting()
        self.message_box = MessageBox()
        self.function_manager = FunctionManager()
        self.last_request_time = time.time()
        self.clear_history()
        self.set_function()

    def set_function(self):
        self.function_manager.add_function(TestFunction())
        self.function_manager.add_function(ScheduleFunction())

    async def get_stream_chat(
        self, _message: str, function: bool
    ) -> AsyncIterator[str]:
        self.is_timeout()
        self.message_box.add_message(UserMessage(content=_message))
        chat_type = "stream_function" if function else "stream"
        chat_api = self.container.get_gpt_chat(chat_type)
        try:
            while True:
                collected_messages = AssistanceMessage()
                async for chat_data in self.get_stream_data(chat_api):
                    collected_messages += chat_data
                    yield chat_data.content

                if chat_data.finish_reason == AssistanceMessage.NULL:
                    break
                elif chat_data.finish_reason == AssistanceMessage.FUNCTION_CALL:
                    yield f"\ncall function: {collected_messages.function_call}\n"
                    function_message = await self.function_manager.run(
                        collected_messages
                    )
                    self.message_box.add_message(function_message)
                elif chat_data.finish_reason == AssistanceMessage.STOP:
                    break
                elif chat_data.finish_reason == AssistanceMessage.LENGHT:
                    pass
                elif chat_data.finish_reason == AssistanceMessage.CONTENT_FILTER:
                    logger.warning("content filter")
                    logger.warning(f"content: {collected_messages}")
                    yield "\ncontent filter\n"
                    break
                else:
                    break
        except OpenaiApiError as e:
            yield e.message

    async def get_stream_chat_with_function(self, _message: str) -> AsyncIterator[str]:
        self.is_timeout()
        self.message_box.add_message(UserMessage(content=_message))
        chat_api = self.container.get_gpt_chat("stream_function")
        call_functions = []
        function_data = self.function_manager.make_dict()
        while True:
            messages = self.message_box.make_messages(setting=self.setting)
            collected_messages = AssistanceMessage()
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

    async def get_stream_data(
        self, chat_api: BaseChat
    ) -> AsyncIterator[AssistanceMessage]:
        messages = self.message_box.make_messages(setting=self.setting)
        function_data = self.function_manager.make_dict()
        collected_messages = AssistanceMessage()
        logger.info(f"message: {messages}")
        async for data in chat_api.run(
            messages, function=function_data, setting=self.setting
        ):
            temp_messages = AssistanceMessage(data=data)
            yield temp_messages
            collected_messages += temp_messages
        logger.info(f"request: {collected_messages}")
        self.message_box.add_message(collected_messages)

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
        if time.time() - self.last_request_time > self.setting.keep_min * 60:
            self.clear_history()
        self.last_request_time = time.time()

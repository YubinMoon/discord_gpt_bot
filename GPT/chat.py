import aiohttp
import logging
import json
import httpx
from typing import AsyncIterator
from httpx._models import Response
from .message import MessageBox
from .setting import Setting
from . import openai

logger = logging.getLogger(__name__)


class Chat:
    def __init__(self, api_key: str, openai_api: openai.Chat):
        self.openai_api = openai_api
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    async def run(
        self, messages: list[dict[str, str]] | MessageBox, setting: Setting
    ) -> str:
        self.data = self.make_data(messages=messages, setting=setting)
        resp = await self.openai_api.create(header=self.header, data=self.data)
        return resp["choices"][0]["message"]["content"]

    def make_data(self, messages: list[dict[str, str]] | MessageBox, setting: Setting):
        if isinstance(messages, MessageBox):
            messages = messages.make_messages(setting=setting)
        return {
            "model": setting.model,
            "messages": messages,
            "temperature": setting.temperature,
            "top_p": setting.top_p,
        }


class ChatStream(Chat):
    def __init__(self, api_key: str, openai_api: openai.Chat):
        super().__init__(api_key=api_key, openai_api=openai_api)

    async def run(
        self, messages: list[dict[str, str]], setting: Setting
    ) -> AsyncIterator[dict[str, str | dict[str, str]]]:
        self.data = self.make_data(messages=messages, setting=setting)
        async for data in self.openai_api.create(header=self.header, data=self.data):
            yield data["choices"][0]

    def make_data(self, messages: list[dict[str, str]], setting: Setting):
        data = super().make_data(messages=messages, setting=setting)
        data["stream"] = True
        return data


class ChatStreamFunction(ChatStream):
    def __init__(self, api_key: str, openai_api: openai.Chat):
        super().__init__(api_key=api_key, openai_api=openai_api)

    async def run(
        self, messages: list[dict[str, str]], function: list, setting: Setting
    ) -> AsyncIterator[dict[str, str | dict[str, str]]]:
        self.function = function
        async for message in super().run(messages=messages, setting=setting):
            yield message

    def make_data(self, messages: list[dict[str, str]], setting: Setting):
        data = super().make_data(messages=messages, setting=setting)
        data["functions"] = self.function
        data["function_call"] = "auto"
        return data

import aiohttp
import logging
import json
import httpx
from httpx._models import Response
from functools import wraps
from .message import MessageBox
from .setting import Setting
from typing import AsyncIterator

logger = logging.getLogger(__name__)


class ChatAPIError(Exception):
    pass


class Chat:
    def __init__(self, api_key: str):
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    async def run(
        self, messages: list[dict[str, str]] | MessageBox, setting: Setting
    ) -> str:
        self.data = self.make_data(messages=messages, setting=setting)
        return await self.chat_request()

    async def chat_request(self) -> str:
        async with httpx.AsyncClient(timeout=None) as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=self.data,
            )
            resp = response.json()
            if "error" in resp:
                raise ChatAPIError(resp.get("error"))
            return resp.get("choices")[0].get("message").get("content")

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
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    async def run(
        self, messages: list[dict[str, str]], setting: Setting
    ) -> AsyncIterator[dict[str, str | dict[str, str]]]:
        self.data = self.make_data(messages=messages, setting=setting)
        async with httpx.AsyncClient(timeout=None) as session:
            async with session.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=self.data,
            ) as response:
                if response.status_code == 400:
                    await self.bad_request(response=response)
                async for resp in self.process_stream_request(resp=response):
                    yield resp

    async def process_stream_request(self, resp: Response) -> AsyncIterator[str]:
        async for chunk in resp.aiter_bytes():
            chunk_str = chunk.decode("utf-8")
            async for resp in self.get_data_from_chunk(chunk_str=chunk_str):
                yield resp

    async def get_data_from_chunk(self, chunk_str: str) -> AsyncIterator[str]:
        response_data = chunk_str.split("\n\n")
        for data in response_data:
            if data.startswith("data: "):
                data = data[6:]
                if data == "[DONE]":
                    break
                data_dict = json.loads(data)
                try:
                    response = data_dict["choices"][0]
                except KeyError as e:
                    logger.error(data_dict)
                    raise KeyError(e)
                yield response  # {"index":0,"delta":{"role":"assistant","content":""},"finish_reason":"stop"}

    async def bad_request(self, response: Response):
        resp = await response.aread()
        text_data = resp.decode("utf-8")
        data = json.loads(text_data)
        raise ChatAPIError(data.get("error"))

    def make_data(self, messages: list[dict[str, str]], setting: Setting):
        data = super().make_data(messages=messages, setting=setting)
        data["stream"] = True
        return data


class ChatStreamFunction(ChatStream):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

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

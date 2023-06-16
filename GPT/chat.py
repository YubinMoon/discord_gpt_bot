import aiohttp
import logging
import json
import httpx
from functools import wraps

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

    async def run(self, messages: list[dict[str, str]], setting: Setting) -> str:
        self.data = self.make_data(messages=messages, setting=setting)
        return await self.chat_request()

    async def chat_request(self) -> str:
        async with httpx.AsyncClient() as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=self.data,
            )
            resp = response.json()
            if "error" in resp:
                raise ChatAPIError(resp.get("error"))
            return resp.get("choices")[0].get("message").get("content")

    def make_data(self, messages: list[dict[str, str]], setting: Setting):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=self.data,
            ) as response:
                if response.status == 400:
                    await self.bad_request(response=response)
                # 스트림의 응답을 처리합니다.
                async for resp in self.process_stream_request(resp=response):
                    yield resp

    async def process_stream_request(
        self, resp: aiohttp.ClientResponse
    ) -> AsyncIterator[str]:
        async for chunk in resp.content.iter_any():
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
                response = data_dict["choices"][0]
                yield response  # {"index":0,"delta":{"role":"assistant","content":""},"finish_reason":"stop"}

    async def bad_request(self, response: aiohttp.ClientResponse):
        resp = await response.json()
        raise ChatAPIError(resp.get("error"))

    def make_data(self, messages: list[dict[str, str]], setting: Setting):
        data = super().make_data(messages=messages, setting=setting)
        data["stream"] = True
        return data


async def stream_chat_request(headers: dict, data: dict) -> AsyncIterator[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
        ) as response:
            # 스트림의 응답을 처리합니다.
            async for response in process_stream_request(response=response):
                yield response


async def process_stream_request(
    response: aiohttp.ClientResponse,
) -> AsyncIterator[str]:
    async for chunk in response.content.iter_chunks():
        # 두 줄로 나눕니다.
        if not chunk[1]:
            logger.error(chunk)
            raise Exception("청크 false Error")
        chunk_str = chunk[0].decode("utf-8")
        async for response in get_data_from_chunk(chunk_str=chunk_str):
            yield response


async def get_data_from_chunk(chunk_str: str) -> AsyncIterator[str]:
    response_data = chunk_str.split("\n\n")
    for data in response_data:
        if data.startswith("data: "):
            data = data[6:]
            if data == "[DONE]":
                return
            data_dict = json.loads(data)
            response = data_dict["choices"][0]
            yield response  # {"index":0,"delta":{"role":"assistant","content":""},"finish_reason":"stop"}

import aiohttp
import logging
import json
import traceback
from functools import wraps

from .setting import Setting
from typing import AsyncIterator

logger = logging.getLogger(__name__)


def handle_chat_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientConnectionError as e:
            logger.exception(e)
            raise ChatAPIError("API 연결 실패")
        except aiohttp.ClientResponseError as e:
            logger.exception(e)
            raise ChatAPIError("API 응답 오류")
        except ChatAPIError as e:
            logger.exception(e)
            raise e
        except Exception:
            logger.exception(traceback.print_exc())
            raise ChatAPIError("API 에러")

    return wrapper


class ChatAPIError(Exception):
    pass


class Chat:
    def __init__(self, api_key: str):
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    @handle_chat_error
    async def run(self, messages: list[dict[str, str]], setting: Setting) -> str:
        self.data = self.make_data(messages=messages, setting=setting)
        return await self.chat_request()

    async def chat_request(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=self.data,
            ) as response:
                response = await response.json()
                if "error" in response:
                    raise ChatAPIError(response.get("error"))
                return response.get("choices")[0].get("message").get("content")

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
                # 스트림의 응답을 처리합니다.
                async for resp in self.process_stream_request(response=response):
                    yield resp

    async def process_stream_request(
        self, response: aiohttp.ClientResponse
    ) -> AsyncIterator[str]:
        async for chunk in response.content.iter_chunks():
            # 두 줄로 나눕니다.
            if not chunk[1]:
                logger.error(chunk)
                raise Exception("청크 false Error")
            chunk_str = chunk[0].decode("utf-8")
            async for response in self.get_data_from_chunk(chunk_str=chunk_str):
                yield response

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

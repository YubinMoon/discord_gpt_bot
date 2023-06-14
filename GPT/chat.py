import aiohttp
import logging
import json

from typing import Iterator, AsyncGenerator, AsyncIterator

logger = logging.getLogger(__name__)


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

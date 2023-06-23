import json
import httpx
import asyncio
from typing import AsyncIterator


class OpenaiApiError(Exception):
    def __init__(self, response_json: dict[str, str]) -> None:
        self.message: str = response_json["error"]["message"]
        self.type: str = response_json["error"]["type"]

    def __str__(self) -> str:
        return self.message


class Chat:
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> dict[str, str] | AsyncIterator[dict[str, str]]:
        raise NotImplementedError


class ChatCompletion(Chat):
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=None) as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=header,
                json=data,
            )
        if response.status_code != 200:
            raise OpenaiApiError(response.json())
        response_json = response.json()
        return response_json


class ChatStreamCompletion(Chat):
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> AsyncIterator[dict[str, str]]:
        data["stream"] = True
        async with httpx.AsyncClient(timeout=None) as session:
            async with session.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=header,
                json=data,
            ) as response:
                async for chunk in response.aiter_text():
                    for data in self.handle_chunk(chunk):
                        yield data

    def handle_chunk(self, chunk: str) -> list[dict[str, str]]:
        for data in chunk.split("\n\n"):
            if data.startswith("data: ") and data[6:] != "[DONE]":
                yield json.loads(data[6:])
            elif "error" in data:
                data = json.loads(data)
                raise OpenaiApiError(data)

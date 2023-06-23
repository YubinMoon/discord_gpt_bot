import httpx
from typing import AsyncIterator
from . import OpenaiApiClientInterface, OpenaiApiStreamClientInterface
from ..error import ChatAPIError


class BasicClient:
    def __init__(self, api_key) -> None:
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }


class OpenaiApiClient(BasicClient, OpenaiApiClientInterface):
    def __init__(self, api_key) -> None:
        super().__init__(api_key=api_key)

    async def get_request(self, data: dict[str, str]) -> httpx.Response:
        async with httpx.AsyncClient(timeout=None) as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=data,
            )
            return response


class OpenaiApiStreamClient(BasicClient, OpenaiApiStreamClientInterface):
    def __init__(self, api_key) -> None:
        super().__init__(api_key=api_key)

    async def get_get_request(
        self, data: dict[str, str]
    ) -> AsyncIterator[httpx.Response]:
        async with httpx.AsyncClient(timeout=None) as session:
            async with session.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=self.header,
                json=data,
            ) as response:
                yield response

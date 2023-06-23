import httpx
from typing import AsyncIterator


class OpenaiApiClientInterface:
    async def get_request(self, data: dict[str, str]) -> httpx.Response:
        raise NotImplementedError


class OpenaiApiStreamClientInterface:
    async def get_get_request(
        self, data: dict[str, str]
    ) -> AsyncIterator[httpx.Response]:
        raise NotImplementedError

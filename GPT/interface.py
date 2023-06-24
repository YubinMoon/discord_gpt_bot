from __future__ import annotations
import copy
from typing import AsyncIterator
from .setting import Setting


class BaseOpenaiApi:
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> dict[str, str] | AsyncIterator[dict[str, str]]:
        raise NotImplementedError


class BaseMessage:
    def __init__(self, content: str):
        self.role: str = ""
        self.content: str = content if content else ""

    def make_message(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def __str__(self) -> str:
        return (
            f"< {self.__class__.__name__} role: {self.role}, content: {self.content} >"
        )

    def __add__(self, other: BaseMessage) -> BaseMessage:
        temp = copy.deepcopy(self)
        temp.content += other.content
        return temp


class BaseChat:
    async def run(
        self,
        messages: list[dict[str, str]] | BaseMessage,
        setting: Setting,
        function: list = None,
    ) -> str:
        raise NotImplementedError


class BaseClient:
    pass


class BaseContainer:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_gpt_client(self, id: int | str) -> BaseClient:
        raise NotImplementedError

    def get_gpt_chat(self, type: str) -> BaseChat:
        raise NotImplementedError

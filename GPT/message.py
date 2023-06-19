from __future__ import annotations
import logging
import copy
from typing import Any
from .token import Tokener
from .setting import Setting

logger = logging.getLogger(__name__)


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


class SystemMessage(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content=content)
        self.role = "system"


class UserMessage(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content=content)
        self.role = "user"


class AssistanceMessage(BaseMessage):
    NULL: str = "null"
    STOP: str = "stop"
    LENGHT: str = "length"
    FUNCTION_CALL: str = "function_call"
    CONTENT_FILTER: str = "content_filter"

    def __init__(self, data: dict[str, dict[str, str] | str] = {}):
        delta = data.get("delta", {})
        super().__init__(content=delta.get("content"))
        self.function_call = delta.get("function_call", {})
        self.finish_reason = data.get("finish_reason", "null")
        self.role = "assistant"

    def make_message(self) -> dict[str, str]:
        message = super().make_message()
        if self.function_call:
            message["function_call"] = self.function_call
        return message

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} role: {self.role}, content: {self.content}, function_call: {self.function_call} finish_reason: {self.finish_reason} >"

    def __add__(self, other: AssistanceMessage) -> AssistanceMessage:
        temp = copy.deepcopy(self)
        temp.content += other.content
        if other.finish_reason != self.NULL:
            temp.finish_reason = other.finish_reason
        for key, value in other.function_call.items():
            if key in temp.function_call:
                temp.function_call[key] += value
            else:
                temp.function_call[key] = value
        return temp


class FunctionMessage(BaseMessage):
    def __init__(self, name: str, content: Any):
        super().__init__(content=str(content))
        self.role = "function"
        self.name = name

    def make_message(self) -> dict[str, str]:
        message = super().make_message()
        message["name"] = self.name
        return message

    def __str__(self):
        return f"< {self.__class__.__name__} role: {self.role}, content: {self.content} name: {self.name} >"

    def __add__(self, other: FunctionMessage) -> FunctionMessage:
        temp = copy.deepcopy(self)
        temp.content += other.content
        temp.name = other.name
        return temp


class MessageBox:
    def __init__(self):
        self.messaes: list[BaseMessage] = []

    def add_message(self, message: BaseMessage):
        self.messaes.append(message)

    def make_messages(self, setting: Setting | None = None) -> list[dict[str, str]]:
        messages = []
        if not setting:
            return [message.make_message() for message in self.messaes]
        while self.get_token(setting) > setting.max_token:
            self.messaes = self.messaes[1:]
        if setting.system_text:
            messages = [
                SystemMessage(content=setting.system_text),
            ]
        messages.extend(self.messaes)
        return self.convert_messages(messages)

    def get_token(self, setting: Setting | None = None) -> int:
        if not setting.system_text:
            return Tokener.num_tokens_from_messages(
                messages=self.convert_messages(messages=self.messaes),
            )
        return Tokener.num_tokens_from_messages(
            messages=self.convert_messages(
                messages=[
                    SystemMessage(content=setting.system_text),
                    *self.messaes,
                ]
            ),
            model=setting.model,
        )

    def convert_messages(self, messages: list[BaseMessage]) -> list[dict[str, str]]:
        return [message.make_message() for message in messages]

    def clear(self):
        self.messaes.clear()

    def __len__(self):
        return len(self.messaes)

    def __getitem__(self, idx) -> BaseMessage:
        return self.messaes[idx]

    def __str__(self):
        return f"< MessageBox-{len(self.messaes)} >"

from GPT.openai import ChatCompletion, ChatStreamCompletion
from GPT.chat import Chat, ChatStream, ChatStreamFunction
from GPT.error import OpenaiApiError
from dotenv import load_dotenv
from typing import AsyncIterator
from GPT.client import Client

load_dotenv()
from GPT.container import GPTContainer


class StaticChatCompletion(ChatCompletion):
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> dict[str, str]:
        if not header.get("Authorization"):
            raise OpenaiApiError(
                {
                    "error": {
                        "message": "Missing Authorization header",
                        "type": "invalid_request_error",
                    }
                }
            )
        if not data["messages"]:
            raise OpenaiApiError(
                {
                    "error": {
                        "message": "[] is too short - 'messages'",
                        "type": "invalid_request_error",
                    }
                }
            )
        return {
            "id": "chatcmpl-7UaDtilNOgGAIUSbyoUE7Pp7z5pb8",
            "object": "chat.completion",
            "created": 1687523437,
            "model": "gpt-3.5-turbo-0301",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello there! How can I assist you today?",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 21, "completion_tokens": 10, "total_tokens": 31},
        }


class StaticChatStreamCompletion(ChatStreamCompletion):
    async def create(
        self, header: dict[str, str], data: dict[str, str]
    ) -> AsyncIterator[dict[str, str]]:
        if not header.get("Authorization"):
            raise OpenaiApiError(
                {
                    "error": {
                        "message": "Missing Authorization header",
                        "type": "invalid_request_error",
                    }
                }
            )
        if not data["messages"]:
            raise OpenaiApiError(
                {
                    "error": {
                        "message": "[] is too short - 'messages'",
                        "type": "invalid_request_error",
                    }
                }
            )
        result = [
            [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": ""},
                    "finish_reason": None,
                }
            ],
            [{"index": 0, "delta": {"content": "Hi"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " there"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": "!"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " How"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " can"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " I"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " assist"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " you"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": " today"}, "finish_reason": None}],
            [{"index": 0, "delta": {"content": "?"}, "finish_reason": None}],
            [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        ]
        if "functions" in data:
            result = [
                [
                    {
                        "delta": {
                            "content": None,
                            "function_call": {
                                "arguments": "",
                                "name": "get_current_weather",
                            },
                            "role": "assistant",
                        },
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": "{\n"}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": " "}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": ' "'}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": "location"}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": '":'}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": ' "'}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": "Se"}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": "oul"}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": '"\n'}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [
                    {
                        "delta": {"function_call": {"arguments": "}"}},
                        "finish_reason": None,
                        "index": 0,
                    }
                ],
                [{"delta": {}, "finish_reason": "function_call", "index": 0}],
            ]
        for d in result:
            yield {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": d,
            }


class TestContainer(GPTContainer):
    def __init__(self, api_key):
        self.api_key = api_key
        self.Client_container = {}

    def get_gpt_client(self, key: int | str) -> Client:
        if key in self.Client_container:
            return self.Client_container[key]
        else:
            self.Client_container[key] = Client(self)
            return self.Client_container[key]

    def get_gpt_chat(self, type: str) -> Chat:
        if type == "completion":
            openai_api = StaticChatCompletion()
            return Chat(self.api_key, openai_api)
        elif type == "stream":
            openai_api = StaticChatStreamCompletion()
            return ChatStream(self.api_key, openai_api)
        elif type == "stream_function":
            openai_api = StaticChatStreamCompletion()
            return ChatStreamFunction(self.api_key, openai_api)
        else:
            raise ValueError(
                "Invalid type. Valid types are: completion, stream, stream_function"
            )

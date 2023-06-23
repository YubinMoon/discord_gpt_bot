import os
import unittest
from GPT import chat
from GPT.message import (
    MessageBox,
    UserMessage,
    AssistanceMessage,
)
from GPT.openai import ChatCompletion, ChatStreamCompletion
from GPT.error import OpenaiApiError
from dotenv import load_dotenv
from typing import AsyncIterator

load_dotenv()


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
        data = [
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": ""},
                        "finish_reason": None,
                    }
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": "Hi"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " there"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": "!"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " How"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " can"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " I"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " assist"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " you"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": " today"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [
                    {"index": 0, "delta": {"content": "?"}, "finish_reason": None}
                ],
            },
            {
                "id": "chatcmpl-7UaJHztG5CcWva1jVAUcNHS7Wu3ez",
                "object": "chat.completion.chunk",
                "created": 1687523771,
                "model": "gpt-3.5-turbo-0301",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            },
        ]
        for d in data:
            yield d


class ChatTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.messages = [
            {"role": "user", "content": "안녕?"},
        ]
        self.message_box = MessageBox()
        self.message_box.add_message(UserMessage(content="안녕?"))
        self.completion = StaticChatCompletion()
        self.stream = StaticChatStreamCompletion()
        self.chat_api = chat.Chat(api_key=self.api_key, openai_api=self.completion)
        self.stream_api = chat.ChatStream(api_key=self.api_key, openai_api=self.stream)
        self.function_api = chat.ChatStreamFunction(
            api_key=self.api_key, openai_api=self.stream
        )

    async def test_run(self):
        response = await self.chat_api.run(messages=self.messages, setting=self.setting)
        self.assertEqual(response, "Hello there! How can I assist you today?")

    async def test_run_no_messages(self):
        with self.assertRaises(OpenaiApiError) as context:
            await self.chat_api.run(messages=[], setting=self.setting)

    async def test_run_stream(self):
        message = AssistanceMessage()
        async for data in self.stream_api.run(self.messages, self.setting):
            message += AssistanceMessage(data=data)
        self.assertEqual("Hi there! How can I assist you today?", message.content)
        self.assertEqual("stop", message.finish_reason)

    async def test_run_stream_no_message(self):
        message = AssistanceMessage()
        with self.assertRaises(OpenaiApiError) as context:
            async for data in self.stream_api.run([], self.setting):
                message += AssistanceMessage(data=data)


if __name__ == "__main__":
    unittest.main()

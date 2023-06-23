import unittest
import os
from .chat import ChatCompletion, ChatStreamCompletion, OpenaiApiError
from dotenv import load_dotenv
from typing import AsyncIterator

load_dotenv()


class StaticChatCompletion(ChatCompletion):
    @classmethod
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
    @classmethod
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


class ChatCompletionTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        api_key = os.environ["OPENAI_API_KEY"]
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        }

    async def test_chat_completion(self):
        result = await ChatCompletion.create(self.header, self.data)
        self.assertGreater(result["usage"]["total_tokens"], 10)

    async def test_chat_completion_invalid_api_key(self):
        self.header["Authorization"] = f"Beare abcd"
        with self.assertRaises(OpenaiApiError) as context:
            await ChatCompletion.create(self.header, self.data)
        self.assertIn("API key", context.exception.message)

    async def test_completion_invalid_model(self):
        self.data["model"] = "gpt.3"
        with self.assertRaises(OpenaiApiError) as context:
            await ChatCompletion.create(self.header, self.data)
        self.assertIn("model", context.exception.message)

    async def test_stream(self):
        self.data["stream"] = True
        result = []
        async for data in ChatStreamCompletion.create(self.header, self.data):
            self.assertIn("choices", data)
            result.append(data)
        print(result)

    async def test_stream_invalid_api_key(self):
        self.data["stream"] = True
        self.header["Authorization"] = f"Beare abcd"
        with self.assertRaises(OpenaiApiError) as context:
            async for data in ChatStreamCompletion.create(self.header, self.data):
                self.assertIn("choices", data)
        self.assertIn("API key", context.exception.message)

    async def test_stream_invalid_model(self):
        self.data["stream"] = True
        self.data["model"] = "gpt.3"
        with self.assertRaises(OpenaiApiError) as context:
            async for data in ChatStreamCompletion.create(self.header, self.data):
                self.assertIn("choices", data)
        self.assertIn("model", context.exception.message)


if __name__ == "__main__":
    unittest.main()

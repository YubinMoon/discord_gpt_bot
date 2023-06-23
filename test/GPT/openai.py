import unittest
import os
from GPT.openai import ChatCompletion, ChatStreamCompletion
from GPT.error import OpenaiApiError
from dotenv import load_dotenv
from typing import AsyncIterator

load_dotenv()


def make_dummy_function() -> list:
    return [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                    },
                },
                "required": ["location"],
            },
        }
    ]


class ChatCompletionTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        api_key = os.environ["OPENAI_API_KEY"]
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.data = {
            "model": "gpt-3.5-turbo-0613",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        }
        self.completion = ChatCompletion()
        self.stream = ChatStreamCompletion()

    async def test_chat_completion(self):
        result = await self.completion.create(self.header, self.data)
        self.assertGreater(result["usage"]["total_tokens"], 10)

    async def test_chat_completion_invalid_api_key(self):
        self.header["Authorization"] = f"Beare abcd"
        with self.assertRaises(OpenaiApiError) as context:
            await self.completion.create(self.header, self.data)
        self.assertIn("API key", context.exception.message)

    async def test_completion_invalid_model(self):
        self.data["model"] = "gpt.3"
        with self.assertRaises(OpenaiApiError) as context:
            await self.completion.create(self.header, self.data)
        self.assertIn("model", context.exception.message)

    async def test_completion_empty_messages(self):
        self.data["messages"] = []
        with self.assertRaises(OpenaiApiError) as context:
            await self.completion.create(self.header, self.data)
        self.assertIn("messages", context.exception.message)

    async def test_stream(self):
        self.data["stream"] = True
        async for data in self.stream.create(self.header, self.data):
            self.assertIn("choices", data)

    async def test_stream_invalid_api_key(self):
        self.data["stream"] = True
        self.header["Authorization"] = f"Beare abcd"
        with self.assertRaises(OpenaiApiError) as context:
            async for data in self.stream.create(self.header, self.data):
                self.assertIn("choices", data)
        self.assertIn("API key", context.exception.message)

    async def test_stream_invalid_model(self):
        self.data["stream"] = True
        self.data["model"] = "gpt.3"
        with self.assertRaises(OpenaiApiError) as context:
            async for data in self.stream.create(self.header, self.data):
                self.assertIn("choices", data)
        self.assertIn("model", context.exception.message)

    async def test_stream_function(self):
        self.data["stream"] = True
        self.data["functions"] = make_dummy_function()
        async for data in self.stream.create(self.header, self.data):
            self.assertIn("choices", data)


if __name__ == "__main__":
    unittest.main()

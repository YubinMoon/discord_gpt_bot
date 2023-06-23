import unittest
import os
from .chat import ChatCompletion, ChatStreamCompletion, OpenaiApiError
from dotenv import load_dotenv

load_dotenv()


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
        async for data in ChatStreamCompletion.create(self.header, self.data):
            self.assertIn("choices", data)

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

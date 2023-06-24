import os
import unittest
from GPT.client import Client
from GPT.message import BaseMessage, AssistanceMessage
from dotenv import load_dotenv
from .mock import TestContainer

load_dotenv()


class ClientTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        api_key = os.environ["OPENAI_API_KEY"]
        container = TestContainer(api_key)
        self.client = container.get_gpt_client("test")

    async def test_stream_chat(self):
        message = AssistanceMessage()
        async for msg in self.client.get_stream_chat("안녕?"):
            message = msg
        self.assertEqual("Hi there! How can I assist you today?", message.content)
        self.assertEqual("stop", message.finish_reason)

    async def test_stream_chat_no_message(self):
        message = AssistanceMessage()
        async for msg in self.client.get_stream_chat(""):
            message = msg
        self.assertEqual("Hi there! How can I assist you today?", message.content)
        self.assertEqual("stop", message.finish_reason)

    # async def test_short_chat(self):
    #     result = await self.client.short_chat("안녕?", "당신은 친절한 AI 입니다.")
    #     self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()

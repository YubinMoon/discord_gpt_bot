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
            message += msg
            print(message)

    # async def test_short_chat(self):
    #     chat = gpt.GPT(api_key=self.api_key)
    #     result = await chat.short_chat("안녕?", "당신은 친절한 AI 입니다.")
    #     self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()

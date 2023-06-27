import os
import unittest
from GPT.error import OpenaiApiError
from GPT.client import Client
from GPT.message import BaseMessage, AssistanceMessage
from dotenv import load_dotenv
from .mock import TestContainer, RaiseContainer, ErrorContainer

load_dotenv()


class ClientTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        api_key = os.environ["OPENAI_API_KEY"]
        container = TestContainer(api_key)
        raise_container = RaiseContainer(api_key)
        error_container = ErrorContainer(api_key)
        self.client = container.get_gpt_client("test")
        self.raise_client = raise_container.get_gpt_client("test")
        self.error_client = error_container.get_gpt_client("test")

    async def test_stream_chat(self):
        message = ""
        async for msg in self.client.get_stream_chat("안녕?"):
            message += msg
        self.assertEqual("Hi there! How can I assist you today?", message)

    async def test_stream_chat_no_message(self):
        message = ""
        async for msg in self.client.get_stream_chat(""):
            message += msg
        self.assertEqual("Hi there! How can I assist you today?", message)

    async def test_stream_chat_raise(self):
        message = ""
        async for msg in self.raise_client.get_stream_chat("안녕?"):
            message += msg
        print(message)


if __name__ == "__main__":
    unittest.main()

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
from .container import TestContainer

load_dotenv()


class ChatTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.messages = [
            {"role": "user", "content": "안녕?"},
        ]
        self.message_box = MessageBox()
        self.message_box.add_message(UserMessage(content="안녕?"))

        container = TestContainer(self.api_key)
        self.chat_api = container.get_gpt_chat("completion")
        self.stream_api = container.get_gpt_chat("stream")
        self.function_api = container.get_gpt_chat("stream_function")

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

    async def test_run_stream_function(self):
        self.message_box.add_message(UserMessage(content="오늘 날씨 어때?"))
        message = AssistanceMessage()
        async for data in self.function_api.run(
            self.message_box, self.setting, ["functions"]
        ):
            message += AssistanceMessage(data=data)
        self.assertEqual(message.finish_reason, "function_call")


if __name__ == "__main__":
    unittest.main()

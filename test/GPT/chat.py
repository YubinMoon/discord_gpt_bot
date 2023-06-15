import os
from unittest import TestCase, IsolatedAsyncioTestCase
from GPT import chat
from GPT import setting
from GPT.message import MessageLine
from dotenv import load_dotenv

load_dotenv()


class ChatTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.messages = [
            {"role": "user", "content": "안녕?"},
        ]

    async def test_run(self):
        chat_api = chat.Chat(api_key=self.api_key)
        response = await chat_api.run(messages=self.messages, setting=self.setting)
        self.assertGreater(len(response), 0)

    async def test_run_no_messages(self):
        chat_api = chat.Chat(api_key=self.api_key)
        with self.assertRaises(chat.ChatAPIError) as context:
            await chat_api.run(messages=[], setting=self.setting)
        error_dict = context.exception.args[0]
        self.assertEqual(error_dict.get("type"), "invalid_request_error")

    async def test_run_stream(self):
        stream_api = chat.ChatStream(api_key=self.api_key)
        message = MessageLine()
        async for data in stream_api.run(self.messages, self.setting):
            message += MessageLine(data=data)
            print(message)

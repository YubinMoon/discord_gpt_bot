import os
from unittest import IsolatedAsyncioTestCase
from GPT import chat
from GPT.message import MessageLine, MessageBox
from dotenv import load_dotenv

load_dotenv()


class ChatTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.messages = [
            {"role": "user", "content": "안녕?"},
        ]
        self.message_box = MessageBox()
        self.message_box.add_message(MessageLine(role="user", content="안녕?"))

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
        self.assertGreater(len(message.content), 0)

    async def test_run_stream_message_box(self):
        stream_api = chat.ChatStream(api_key=self.api_key)
        message = MessageLine()
        async for data in stream_api.run(self.message_box, self.setting):
            message += MessageLine(data=data)
        self.assertGreater(len(message.content), 0)

    async def test_run_stream_no_message(self):
        stream_api = chat.ChatStream(api_key=self.api_key)
        message = MessageLine()
        with self.assertRaises(chat.ChatAPIError) as context:
            async for data in stream_api.run([], self.setting):
                message += MessageLine(data=data)
        error_dict = context.exception.args[0]
        self.assertEqual(error_dict.get("type"), "invalid_request_error")

    async def test_run_stream_function(self):
        stream_api = chat.ChatStreamFunction(api_key=self.api_key)
        self.message_box.add_message(MessageLine(role="user", content="오늘 날씨 어때?"))
        message = MessageLine()
        async for data in stream_api.run(
            self.message_box, self.make_dummy_function(), self.setting
        ):
            message += MessageLine(data=data)
        self.assertEqual(message.finish_reason, "function_call")

    def make_dummy_function(self) -> list:
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

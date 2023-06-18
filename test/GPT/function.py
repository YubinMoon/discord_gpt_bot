import os
from unittest import IsolatedAsyncioTestCase
from GPT import chat
from GPT.message import (
    BaseMessage,
    MessageBox,
    UserMessage,
    SystemMessage,
    FunctionMessage,
    AssistanceMessage,
)
from GPT.function import FunctionManager, TestFunction
from dotenv import load_dotenv


load_dotenv()


class FunctionTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.messages = [
            {"role": "user", "content": "안녕?"},
        ]
        self.message_box = MessageBox()
        self.message_box.add_message(UserMessage(content="안녕?"))
        self.function_manager = FunctionManager()
        self.function_manager.add_function(TestFunction())

    async def test_function(self):
        function_obj = self.function_manager.make_dict()
        for function in function_obj:
            name = function.get("name")
            parameters = function.get("parameters")
            parameters_type = parameters.get("type")
            self.assertGreater(len(name), 0)
            self.assertGreater(len(parameters_type), 0)

    async def test_function_run(self):
        function_message = AssistanceMessage(
            data={
                "delta": {
                    "content": "",
                    "function_call": {
                        "name": "get_current_weather",
                        "arguments": '{\n  "location": "Seoul, South Korea"\n}',
                    },
                },
                "finish_reason": "function_call",
            }
        )
        result = await self.function_manager.run(function_message)

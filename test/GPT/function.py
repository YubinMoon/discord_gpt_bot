import os
import pprint
from unittest import IsolatedAsyncioTestCase
from GPT import chat
from GPT.message import MessageLine, MessageBox
from GPT.function import FunctionManager
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

    async def test_function(self):
        function_manager = FunctionManager()
        pprint.pprint(function_manager.make_dict())

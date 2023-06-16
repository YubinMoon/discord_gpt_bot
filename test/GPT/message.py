import os
from unittest import TestCase, IsolatedAsyncioTestCase
from GPT import chat
from GPT import setting
from GPT import gpt
from GPT import gptbox
from GPT import message
from GPT import message
from dotenv import load_dotenv

load_dotenv()


class MessageTests(IsolatedAsyncioTestCase):
    data1 = {"delta": {"role": "user", "content": "안녕? "}, "finish_reason": "null"}
    data2 = {"delta": {"role": "user", "content": "아이 졸려"}, "finish_reason": "stop"}
    data3 = {"delta": {"role": "user", "content": "안녕? 아이 졸려"}, "finish_reason": "stop"}

    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.msg_box = message.MessageBox()

    async def test_message_class(self):
        msg1 = message.MessageLine(data=self.data1)
        msg2 = message.MessageLine(data=self.data2)
        msg3 = message.MessageLine(data=self.data3)
        msg2 = msg1 + msg2
        self.assertEqual(msg3.role, msg2.role)
        self.assertEqual(msg3.content, msg2.content)
        self.assertEqual(msg3.finish_reason, msg2.finish_reason)

    async def test_make_message(self):
        msg1 = message.MessageLine(data=self.data1)
        data = msg1.make_message()
        self.assertEqual(data["role"], "user")
        self.assertEqual(data["content"], "안녕? ")

    async def test_message_box(self):
        self.msg_box.add_message(message.MessageLine(data=self.data1))
        self.msg_box.add_message(message.MessageLine(data=self.data2))
        self.msg_box.add_message(message.MessageLine(data=self.data3))
        self.assertEqual(len(self.msg_box), 3)
        msg1 = self.msg_box[1]
        msg2 = self.msg_box[1:][0]
        self.assertEqual(msg1.role, msg2.role)
        self.assertEqual(msg1.content, msg2.content)
        self.assertEqual(msg1.finish_reason, msg2.finish_reason)

    async def test_max_token(self):
        for i in range(200):
            self.msg_box.add_message(message.MessageLine(data=self.data3))
        first = len(self.msg_box.make_messages(setting=self.setting))
        self.setting.set_setting("system_text", "당신은 친절한 AI 입니다.")
        second = len(self.msg_box.make_messages(setting=self.setting))
        self.assertLess(first, 200)
        self.assertNotEqual(first, second)

    async def test_get_token(self):
        self.setting.set_setting("system_text", "당신은 친절한 AI 입니다.")
        for i in range(200):
            self.msg_box.add_message(message.MessageLine(data=self.data3))
        self.assertEqual(self.msg_box.get_token(setting=self.setting), 3419)

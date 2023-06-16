import os
from unittest import TestCase, IsolatedAsyncioTestCase
from GPT import chat
from GPT import setting
from GPT import gpt
from GPT import token
from GPT import message


class TokenTests(TestCase):
    data1 = {"delta": {"role": "user", "content": "안녕? "}, "finish_reason": "null"}
    data2 = {"delta": {"role": "user", "content": "아이 졸려"}, "finish_reason": "stop"}
    data3 = {"delta": {"role": "user", "content": "안녕? 아이 졸려"}, "finish_reason": "stop"}

    def setUp(self):
        self.setting = setting.Setting()
        msg1 = message.MessageLine(data=self.data1)
        msg2 = message.MessageLine(data=self.data2)
        msg3 = message.MessageLine(data=self.data3)
        self.msg_box = message.MessageBox()
        self.msg_box.add_message(msg1)
        self.msg_box.add_message(msg2)
        self.msg_box.add_message(msg3)
        self.message = self.msg_box.make_messages(setting=self.setting)

        self.assertEqual(self.setting.system_text, "")
        self.assertEqual(self.setting.max_token, 3000)
        self.assertEqual(self.setting.temperature, 1.0)
        self.assertEqual(self.setting.top_p, 1.0)
        self.assertEqual(self.setting.keep_min, 10)

    def test_get_token(self):
        token_num = token.Tokener.num_tokens_from_messages(
            self.message, self.setting.model
        )
        self.assertEqual(token_num, 47)

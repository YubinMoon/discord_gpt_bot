import unittest
from GPT import setting
from GPT import token
from GPT import message


class TokenTests(unittest.TestCase):
    data1 = {"delta": {"role": "user", "content": "안녕? "}, "finish_reason": "null"}
    data2 = {"delta": {"role": "user", "content": "아이 졸려"}, "finish_reason": "stop"}
    data3 = {"delta": {"role": "user", "content": "안녕? 아이 졸려"}, "finish_reason": "stop"}

    def setUp(self):
        self.setting = setting.Setting()
        self.msg1 = message.AssistanceMessage(data=self.data1)
        self.msg2 = message.AssistanceMessage(data=self.data2)
        self.msg3 = message.AssistanceMessage(data=self.data3)
        self.msg_box = message.MessageBox()

    def test_get_token(self):
        self.msg_box.add_message(self.msg1)
        self.msg_box.add_message(self.msg2)
        self.message = self.msg_box.make_messages(setting=self.setting)
        token_num = token.Tokener.num_tokens_from_messages(
            self.message, self.setting.model
        )
        self.assertEqual(token_num, 25)
        self.msg_box.add_message(self.msg3)
        self.message = self.msg_box.make_messages(setting=self.setting)
        token_num = token.Tokener.num_tokens_from_messages(
            self.message, self.setting.model
        )
        self.assertEqual(token_num, 42)


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from GPT import chat
from GPT import message
from dotenv import load_dotenv

load_dotenv()


class MessageTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(self):
        self.usr_content1 = "안녕? "
        self.usr_content2 = "오늘 날씨 어때?"
        self.usr_msg1 = message.UserMessage(content=self.usr_content1)
        self.usr_msg2 = message.UserMessage(content=self.usr_content2)

        self.sys_content1 = "당신은 친절한 AI 입니다."
        self.sys_content2 = "당신은 불친절한 AI 입니다."
        self.sys_msg1 = message.SystemMessage(content=self.sys_content1)
        self.sys_msg2 = message.SystemMessage(content=self.sys_content2)

        self.asi_content1 = "안녕? "
        self.asi_content2 = "아이 졸려"
        self.asi_msg1 = message.AssistanceMessage(
            data={
                "delta": {"role": "user", "content": self.asi_content1},
                "finish_reason": "null",
            }
        )
        self.asi_msg2 = message.AssistanceMessage(
            data={
                "delta": {"role": "user", "content": self.asi_content2},
                "finish_reason": "stop",
            }
        )

    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.setting = chat.Setting()
        self.msg_box = message.MessageBox()

    async def test_message_class(self):
        self.assertEqual(self.usr_msg1.role, "user")
        self.assertEqual(self.usr_msg1.content, self.usr_content1)
        self.assertEqual(self.usr_msg2.content, self.usr_content2)

        self.assertEqual(self.sys_msg1.role, "system")
        self.assertEqual(self.sys_msg1.content, self.sys_content1)
        self.assertEqual(self.sys_msg2.content, self.sys_content2)

        self.assertEqual(self.asi_msg1.role, "assistant")
        self.assertEqual(self.asi_msg1.content, self.asi_content1)
        self.assertEqual(self.asi_msg2.content, self.asi_content2)

    async def test_message_add(self):
        usr_msg = self.usr_msg1 + self.usr_msg2
        self.assertEqual(usr_msg.content, self.usr_content1 + self.usr_content2)

        sys_msg = self.sys_msg1 + self.sys_msg2
        self.assertEqual(sys_msg.content, self.sys_content1 + self.sys_content2)

        asi_msg = self.asi_msg1 + self.asi_msg2
        self.assertEqual(asi_msg.content, self.asi_content1 + self.asi_content2)
        self.assertEqual(asi_msg.finish_reason, "stop")

    async def test_make_message(self):
        data = self.usr_msg1.make_message()
        self.assertEqual(data["role"], "user")
        self.assertEqual(data["content"], self.usr_content1)

        data = self.sys_msg1.make_message()
        self.assertEqual(data["role"], "system")
        self.assertEqual(data["content"], self.sys_content1)

        data = self.asi_msg1.make_message()
        self.assertEqual(data["role"], "assistant")
        self.assertEqual(data["content"], self.asi_content1)

    async def test_message_box(self):
        self.msg_box.add_message(self.usr_msg1)
        self.msg_box.add_message(self.asi_msg1)
        self.msg_box.add_message(self.sys_msg1)
        self.assertEqual(len(self.msg_box), 3)
        msg1 = self.msg_box[1]
        msg2 = self.msg_box[1:][0]
        self.assertEqual(msg1.role, msg2.role)
        self.assertEqual(msg1.content, msg2.content)
        self.assertEqual(msg1.finish_reason, msg2.finish_reason)

    async def test_max_token(self):
        for i in range(200):
            self.msg_box.add_message(self.usr_msg1)
        self.setting.max_token = 200
        first = len(self.msg_box.make_messages(setting=self.setting))
        self.setting.set_setting("system_text", "당신은 친절한 AI 입니다.")
        second = len(self.msg_box.make_messages(setting=self.setting))
        self.assertEqual(first, 18)
        self.assertEqual(second, 19)

    async def test_get_token(self):
        self.setting.set_setting("system_text", "당신은 친절한 AI 입니다.")
        for i in range(200):
            self.msg_box.add_message(self.usr_msg1)
        self.assertEqual(self.msg_box.get_token(setting=self.setting), 2219)


if __name__ == "__main__":
    unittest.main()

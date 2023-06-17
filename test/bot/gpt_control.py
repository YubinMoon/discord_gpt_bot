import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock, mock_open, patch
from bot import gpt_control
from discord import Message
from GPT.message import MessageLine


class GptControlTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        gpt = AsyncMock()
        gpt.short_chat.return_value = "test.txt"
        self.isdir = Mock()
        self.isdir.return_value = False
        self.mkdir = Mock()
        self.mkdir.return_value = None
        self.msg = AsyncMock()
        self.msg.edit.return_value = None
        self.msg.add_files.return_value = None
        self.discord_message = AsyncMock()
        self.discord_message.id = 1
        self.discord_message.author.nick = "test"
        self.discord_message.content = "안녕?"
        self.discord_message.reply.return_value = self.msg

    # async def test_discord_chat(self):
    #     await gpt_control.ChatHandler(self.discord_message).run()
    #     self.discord_message.reply.assert_called_once_with("대답 중...")
    #     self.msg.edit.assert_called()
    #     self.assertGreater(len(self.msg.edit.call_args.kwargs["content"]), 5)

    # async def test_long_message(self):
    #     handler = gpt_control.ChatHandler(self.discord_message)
    #     handler.msg = self.msg

    #     with patch("os.path.isdir", self.isdir) as mock_isdir:
    #         with patch("os.mkdir", self.mkdir) as mock_mkdir:
    #             with patch("builtins.open", mock_open(read_data="data")) as mock_file:
    #                 await handler.send_to_file()
    #     mock_isdir.assert_called_once_with("temp")
    #     mock_mkdir.assert_called_once_with("temp")
    #     mock_file.assert_called()
    #     self.msg.add_files.assert_called()

    async def test_config(self):
        setting_text = '```{\n  "model": "gpt-3.5-turbo-0613",\n  "system_text": "",\n  "max_token": 3000,\n  "temperature": 1.0,\n  "top_p": 1.0,\n  "keep_min": 10\n}```'
        handler = gpt_control.ConfigHandler(self.discord_message)
        await handler.run()
        self.assertEqual(self.discord_message.reply.call_args.args[0], setting_text)

    async def test_get_config(self):
        setting_list = '```{\n  "model": "gpt-3.5-turbo-0613",\n  "system_text": "",\n  "max_token": 3000,\n  "temperature": 1.0,\n  "top_p": 1.0,\n  "keep_min": 10\n}```'
        setting_list = {
            "model": '```"gpt-3.5-turbo-0613"```',
            "system_text": '```""```',
            "max_token": "```3000```",
            "temperature": "```1.0```",
            "top_p": "```1.0```",
            "keep_min": "```10```",
        }
        handler = gpt_control.ConfigHandler(self.discord_message)
        for key, value in setting_list.items():
            await handler.run(key)
            self.assertEqual(self.discord_message.reply.call_args.args[0], value)

    async def test_set_config(self):
        setting_list = {
            "model": ["gpt-3.5", "```model: gpt-3.5```"],
            "system_text": ["asdf", "```system_text: asdf```"],
            "max_token": ["1000", "```max_token: 1000```"],
            "temperature": ["2.0", "```temperature: 2.0```"],
        }
        handler = gpt_control.ConfigHandler(self.discord_message)
        for key, value in setting_list.items():
            await handler.run(key, value[0])
            self.assertEqual(self.discord_message.reply.call_args.args[0], value[1])

    async def test_role(self):
        handler = gpt_control.RoleHandler(self.discord_message)
        await handler.run()
        self.assertEqual(self.discord_message.reply.call_args.args[0], "역할 정보가 변경되었어요.")
        await handler.run("asdf")
        self.assertEqual(self.discord_message.reply.call_args.args[0], "역할 정보가 변경되었어요.")

    async def test_history(self):
        handler = gpt_control.HistoryHandler(self.discord_message)
        await handler.run()
        self.assertEqual(
            self.discord_message.reply.call_args.args[0], "기록이 없어요. \n대화를 시작해 볼까요?"
        )
        await handler.run("clear")
        self.assertEqual(
            self.discord_message.reply.call_args.args[0], "기록이 없어요. \n대화를 시작해 볼까요?"
        )
        handler.gpt.message_box.add_message(MessageLine(role="asdf", content="asdf"))
        await handler.run()
        self.assertNotEqual(
            self.discord_message.reply.call_args.args[0], "기록이 없어요. \n대화를 시작해 볼까요?"
        )
        await handler.run("clear")
        self.assertEqual(self.discord_message.reply.call_args.args[0], "기억을 초기화 했어요.")

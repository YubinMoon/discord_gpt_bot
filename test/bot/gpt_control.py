import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock
from bot import gpt_control
from discord import Message


class GptControlTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.msg = Mock()
        self.msg.edit.return_value = None
        self.msg.add_files.return_value = None
        self.discord_message = AsyncMock()
        self.discord_message.id = 1
        self.discord_message.author.nick = "test"
        self.discord_message.content = "안녕?"
        self.discord_message.reply.return_value = self.msg

    async def test_discord_chat(self):
        await gpt_control.ChatHandler(self.discord_message).run()
        self.discord_message.reply.assert_called_once_with("대답 중...")
        self.msg.edit.assert_called()
        self.assertGreater(len(self.msg.edit.call_args.kwargs["content"]), 5)

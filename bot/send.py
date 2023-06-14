import logging
import time
import discord
from GPT import GPT, GPTBox
from .utils import handle_errors
from discord_setting import gpt_container

logger = logging.getLogger(__name__)


class SendByWord:
    def __init__(self, message: discord.Message):
        self.text: str = ""
        self.now: int = 0
        self.message: discord.Message = message
        self.msg: discord.Message
        self.gpt: GPT = gpt_container.get_gpt(message.channel.id)

    @handle_errors("GPT가 혀를 깨물었어요...")
    async def send(self):
        self.msg = await self.message.reply("대답 중...")
        logger.info(
            f"name: {self.message.author.nick} - request: {self.message.content}"
        )
        await self.get_from_gpt_and_send_by_word()

        if 1 < len(self.text) < 1900:
            await self.msg.edit(content=self.text)
        if 1900 <= len(self.text):
            await self.msg.add_files()
        return

    async def get_from_gpt_and_send_by_word(self):
        async for text in self.gpt.get_stream_chat(self.message.content):
            self.text += text
            await self.send_after_timer()

    async def send_after_timer(self):
        if time.time() - self.now > 1:
            await self.send_by_word()

    async def send_by_word(self):
        self.now = time.time()
        if 1 < len(self.text) < 1900:
            await self.msg.edit(content=self.text)
        elif 1900 <= len(self.text):
            await self.msg.edit(content=self.text[:1900] + "...")

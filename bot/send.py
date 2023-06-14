import logging
import time
import discord
import os
from GPT import GPT
from .utils import handle_errors
from discord_setting import gpt_container

logger = logging.getLogger(__name__)
MAX_TEXT_LENGTH = 1900


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

        if 1 < len(self.text) < MAX_TEXT_LENGTH:
            await self.msg.edit(content=self.text)
        if MAX_TEXT_LENGTH <= len(self.text):
            await self.send_to_file()
            await self.msg.edit(content="")

    async def get_from_gpt_and_send_by_word(self):
        async for text in self.gpt.get_stream_chat(self.message.content):
            self.text += text
            await self.send_after_timer()

    async def send_after_timer(self):
        if time.time() - self.now > 1:
            await self.send_by_word()

    async def send_by_word(self):
        self.now = time.time()
        if 1 < len(self.text) < MAX_TEXT_LENGTH:
            await self.msg.edit(content=self.text)
        elif MAX_TEXT_LENGTH <= len(self.text):
            await self.msg.edit(content=self.text[:MAX_TEXT_LENGTH] + "...")

    async def send_to_file(self):
        file_name = await self.gpt.short_chat(
            f"'{self.message.content}' I need a file name to save the following question in a file. Please suggest an English file name within 10 characters. The file extension should be .txt!",
            "I am an AI that generates file names summarizing the content.",
        )
        if ".txt" not in file_name:
            file_name += ".txt"
        file_path = "temp/" + file_name
        if not os.path.isdir("temp"):
            os.mkdir("temp")
        logger.info(f"make file: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.text.replace(". ", ".\n"))
        await self.msg.add_files(discord.File(file_path, filename=file_name))

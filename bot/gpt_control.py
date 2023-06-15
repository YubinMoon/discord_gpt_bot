import logging
import time
import discord
from discord.ext import commands
import os
from GPT import GPT
from discord_setting import gpt_container
from .utils import HandleErrors

logger = logging.getLogger(__name__)
MAX_TEXT_LENGTH = 1900


class CommandHandler:
    def __init__(self, discord_message: discord.Message):
        self.discord_message: discord.Message = discord_message
        self.gpt: GPT = gpt_container.get_gpt(discord_message.channel.id)


class SendByWord(CommandHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)
        self.text: str = ""
        self.now: int = 0
        self.msg: discord.Message

    @HandleErrors("설정 변경 중 에러가 발생했어요!")
    async def send(self):
        self.msg = await self.discord_message.reply("대답 중...")
        logger.info(
            f"name: {self.discord_message.author.nick} - request: {self.discord_message.content}"
        )
        await self.get_from_gpt_and_send_by_word()

        if 1 < len(self.text) < MAX_TEXT_LENGTH:
            await self.msg.edit(content=self.text)
        if MAX_TEXT_LENGTH <= len(self.text):
            await self.send_to_file()
            await self.msg.edit(content="")

    async def get_from_gpt_and_send_by_word(self):
        async for text in self.gpt.get_stream_chat(self.discord_message.content):
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
            f"'{self.discord_message.content}' I need a file name to save the following question in a file. Please suggest an English file name within 10 characters. The file extension should be .txt!",
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


class ConfigHandler(CommandHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)


# @handle_errors("config 변경 중 문제가 발생했어요!")
# async def handle_config(ctx: commands.context.Context, *args):
#     gpt = gpt_container.get_gpt(ctx.channel.id)
#     if not args:
#         await ctx.channel.send(f"```{data_to_json(gpt.gloSetting)}```")
#     elif len(args) == 1:
#         key = args[0]
#         if key not in gpt.gloSetting:
#             await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
#         else:
#             value = gpt.gloSetting[key]
#             await ctx.channel.send(f"```{data_to_json(value)}```")
#     elif len(args) == 2:
#         key, value = args[0], args[1]
#         if key not in gpt.gloSetting:
#             await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
#         else:
#             gpt.gloSetting[key] = value
#             gpt.save_setting()
#             await ctx.channel.send(f"```{key}: {value}```")
#     else:
#         await ctx.channel.send("```!gconfig [설정명] [설정값]``` 형태로 입력해주세요.")

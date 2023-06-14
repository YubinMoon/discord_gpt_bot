import discord
from discord.ext import commands
from discord_setting import bot, gpt, bot_prefix
import json
import time
import os
import logging
import discord
import traceback
import discord.errors
from discord.ext import commands
from .utils import handle_errors

logger = logging.getLogger(__name__)


class SendByWord:
    def __init__(self, message: discord.Message):
        self.text: str = ""
        self.now: int = 0
        self.message: discord.Message = message
        self.msg: discord.Message

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
        async for text in gpt.get_stream_chat(self.message.content):
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


async def send_to_gpt(message: discord.Message):
    sendobj = SendByWord(message)
    await sendobj.send()


@bot.event
async def on_ready():
    game = discord.Game("대화에 집중")
    await bot.change_presence(status=discord.Status.online, activity=game)
    logger.info("GPT bot start")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content.startswith(bot_prefix):
        await bot.process_commands(message)
        return

    if "gpt" in message.channel.name:
        await send_to_gpt(message)
        return


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, arg: str):
    ctx.message.content = arg
    await send_to_gpt(ctx.message)


@bot.command(name="clear")
async def clear_history(ctx: discord.Message):
    gpt.clear_history()
    await ctx.channel.send("기억이 초기화되었습니다.")


@bot.command(name="ping")
async def test(ctx: discord.Message, *args):
    await ctx.channel.send("pong!")


@bot.command(name="config")
async def config(ctx: discord.Message, *args):
    await handle_config(ctx, *args)


@handle_errors("config 변경 중 문제가 발생했어요!")
async def handle_config(ctx: discord.Message, *args):
    if not args:
        await ctx.channel.send(f"```{data_to_json(gpt.gloSetting)}```")
    elif len(args) == 1:
        key = args[0]
        if key not in gpt.gloSetting:
            await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
        else:
            value = gpt.gloSetting[key]
            await ctx.channel.send(f"```{data_to_json(value)}```")
    elif len(args) == 2:
        key, value = args[0], args[1]
        if key not in gpt.gloSetting:
            await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
        else:
            gpt.gloSetting[key] = value
            gpt.save_setting()
            await ctx.channel.send(f"```{key}: {value}```")
    else:
        await ctx.channel.send("```!gconfig [설정명] [설정값]``` 형태로 입력해주세요.")


@bot.command(name="role")
async def role_config(ctx: commands.Context, *args):
    await handle_role_config(ctx, *args)


@handle_errors("역할 변경 중 에러가 발생했어요!")
async def handle_role_config(ctx: commands.Context, *args):
    if not args:
        gpt.set_system_text("")
        await ctx.channel.send("역할 정보가 초기화되었습니다.")
    else:
        role_description = " ".join(args)
        gpt.set_system_text(role_description)
        await ctx.channel.send("역할 정보가 설정되었습니다.")


@bot.command(name="history")
async def show_history(ctx: commands.Context):
    await handle_show_history(ctx)


@handle_errors("출력 중 문제가 발생했어요!")
async def handle_show_history(ctx: commands.Context):
    if gpt.history:
        await ctx.channel.send(f"```{data_to_json(gpt.history)}```")
    else:
        await ctx.channel.send("기록이 없어요. \n대화를 시작해 볼까요?")


def data_to_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


@bot.command(name="img")
async def create_image(ctx: commands.Context, *args):
    prompt = " ".join(args)
    await handle_create_image(ctx, prompt)


@handle_errors("이미지 생성 중 문제가 발생했어요!")
async def handle_create_image(ctx: commands.Context, prompt: str):
    msg = await ctx.reply("생성 중...")
    data = await gpt.create_image(prompt=prompt)
    file = discord.File(data, filename=f"{ctx.author.name}.png")
    await msg.edit(content="생성 완료")
    await msg.add_files(file)

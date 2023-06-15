import discord
from discord.ext import commands
from discord_setting import bot, gpt_container, bot_prefix
import json
import logging
import discord
import discord.errors
from .utils import UnValidCommandError, HandleErrors
from .gpt_control import SendByWord
from . import gpt_control

logger = logging.getLogger(__name__)


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
        await SendByWord(message).run()
        return


@bot.command(name="ask")
async def ask(ctx: commands.context.Context, *, arg: str):
    ctx.message.content = arg
    await SendByWord(ctx.message).run()


@bot.command(name="clear")
async def clear_history(ctx: commands.context.Context):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    gpt.clear_history()
    await ctx.channel.send("기억이 초기화되었습니다.")


@bot.command(name="ping")
async def test(ctx: commands.context.Context, *args):
    await ctx.channel.send("pong!")


@bot.command(name="config")
async def config(ctx: commands.context.Context, *args):
    await gpt_control.ConfigHandler(ctx.message).run(*args)


@bot.command(name="role")
async def role_config(ctx: commands.context.Context, *args):
    await gpt_control.RoleHandler(ctx.message).run(*args)


@bot.command(name="history")
async def show_history(ctx: commands.context.Context):
    print(gpt_container)
    await handle_show_history(ctx)


async def handle_show_history(ctx: commands.context.Context):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    if gpt.message_box:
        await ctx.channel.send(f"```{data_to_json(gpt.message_box.make_messages())}```")
    else:
        await ctx.channel.send("기록이 없어요. \n대화를 시작해 볼까요?")


def data_to_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


@bot.command(name="img")
@HandleErrors("이미지 생성 중 문제가 발생했어요!")
async def create_image(ctx: commands.context.Context, *args):
    prompt = " ".join(args)
    await handle_create_image(ctx, prompt)


async def handle_create_image(ctx: commands.context.Context, prompt: str):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    msg = await ctx.reply("생성 중...")
    data = await gpt.create_image(prompt=prompt)
    file = discord.File(data, filename=f"{ctx.author.name}.png")
    await msg.edit(content="생성 완료")
    await msg.add_files(file)

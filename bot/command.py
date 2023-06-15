import discord
from discord.ext import commands
from discord_setting import bot, gpt_container, bot_prefix
import logging
import discord
import discord.errors
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
        await gpt_control.ChatHandler(message).run()
        return


@bot.command(name="ask")
async def ask(ctx: commands.context.Context, *, arg: str):
    ctx.message.content = arg
    await gpt_control.ChatHandler(ctx.message).run()


@bot.command(name="ping")
async def test(ctx: commands.context.Context, *args):
    await ctx.message.reply("pong!")


@bot.command(name="config")
async def config(ctx: commands.context.Context, *args):
    await gpt_control.ConfigHandler(ctx.message).run(*args)


@bot.command(name="role")
async def role_config(ctx: commands.context.Context, *args):
    await gpt_control.RoleHandler(ctx.message).run(*args)


@bot.command(name="history")
async def show_history(ctx: commands.context.Context, *args):
    await gpt_control.HistoryHandler(ctx.message).run(*args)


@bot.command(name="img")
async def create_image(ctx: commands.context.Context, *args):
    await gpt_control.ImageHandler(ctx.message).run(*args)

import discord
from discord.ext import commands
from discord_setting import bot, gpt_container, bot_prefix
import json
import logging
import discord
import discord.errors
from discord.ext import commands
from .utils import handle_errors
from .send import SendByWord

logger = logging.getLogger(__name__)


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
async def ask(ctx: commands.context.Context, *, arg: str):
    ctx.message.content = arg
    await send_to_gpt(ctx.message)


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
    await handle_config(ctx, *args)


@handle_errors("config 변경 중 문제가 발생했어요!")
async def handle_config(ctx: commands.context.Context, *args):
    gpt = gpt_container.get_gpt(ctx.channel.id)
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
async def role_config(ctx: commands.context.Context, *args):
    await handle_role_config(ctx, *args)


@handle_errors("역할 변경 중 에러가 발생했어요!")
async def handle_role_config(ctx: commands.context.Context, *args):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    if not args:
        gpt.set_system_text("")
        await ctx.channel.send("역할 정보가 초기화되었습니다.")
    else:
        role_description = " ".join(args)
        gpt.set_system_text(role_description)
        await ctx.channel.send("역할 정보가 설정되었습니다.")


@bot.command(name="history")
async def show_history(ctx: commands.context.Context):
    print(type(ctx))
    await handle_show_history(ctx)


@handle_errors("출력 중 문제가 발생했어요!")
async def handle_show_history(ctx: commands.context.Context):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    if gpt.message_box:
        await ctx.channel.send(f"```{data_to_json(gpt.message_box.make_messages())}```")
    else:
        await ctx.channel.send("기록이 없어요. \n대화를 시작해 볼까요?")


def data_to_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


@bot.command(name="img")
async def create_image(ctx: commands.context.Context, *args):
    prompt = " ".join(args)
    await handle_create_image(ctx, prompt)


@handle_errors("이미지 생성 중 문제가 발생했어요!")
async def handle_create_image(ctx: commands.context.Context, prompt: str):
    gpt = gpt_container.get_gpt(ctx.channel.id)
    msg = await ctx.reply("생성 중...")
    data = await gpt.create_image(prompt=prompt)
    file = discord.File(data, filename=f"{ctx.author.name}.png")
    await msg.edit(content="생성 완료")
    await msg.add_files(file)

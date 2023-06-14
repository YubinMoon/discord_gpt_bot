import asyncio
import json
import time
import os
import logging
import discord
import traceback
import discord.errors
from discord.ext import commands
from dotenv import load_dotenv

from GPT import GPT

load_dotenv()

LOG_FILENAME = "log.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s \t %(name)s[%(funcName)s:%(lineno)d] - %(message)s",
)
logger = logging.getLogger(__name__)

bot_prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

gpt = GPT(os.environ["OPENAI_API_KEY"])


def handle_errors(error_message):
    def real_decorator(coro):
        async def wrapper(*args, **kwargs):
            try:
                return await coro(*args, **kwargs)
            except NameError:
                logger.exception(traceback.format_exc())
                await args[0].channel.send("GPT가 준비 중 이에요!")
            except:
                logger.exception(traceback.format_exc())
                await args[0].channel.send(error_message)

        return wrapper

    return real_decorator


@handle_errors("GPT 모델 호출 중 오류 발생")
async def gpt_request(message: discord.Message):
    async with message.channel.typing():
        result = await gpt.chat_request(message.content)
        await message.reply(result)


@handle_errors("GPT가 파업을 선언했어요...")
# GPT 스트림 함수
async def send_by_word(message: discord.Message):
    logger.info(f"name: {message.author.nick} - request: {message.content}")

    # 초기값 설정
    text = ""
    now = 0

    msg: discord.Message = await message.reply("대답 중...")
    async for r in gpt.stream_chat_request(message.content):
        text += r
        if len(text) > 1:
            try:
                # 메시지를 일정 간격으로 업데이트
                if time.time() - now > 1:
                    now = time.time()
                    await msg.edit(content=text)
            except discord.errors.HTTPException:
                logger.exception("전송 중 오류 발생")
                logger.exception(text)

    # 최종 응답 메시지 업데이트
    await msg.edit(content=text)


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
        await send_by_word(message)
        return


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, arg: str):
    ctx.message.content = arg
    await send_by_word(ctx.message)


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


TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)

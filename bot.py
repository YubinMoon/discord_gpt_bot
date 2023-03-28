import asyncio
import json
import time
import logging
import discord
import discord.errors
from discord.ext import commands

from gpt import GPT

# 로그 파일 경로 설정
LOG_FILENAME = 'log.log'

# 로그 레벨 설정
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S", encoding="utf-8", format="%(asctime)s - %(levelname)s \t %(name)s[%(funcName)s:%(lineno)d] - %(message)s")

logger = logging.getLogger(__name__)

# 디스코드 봇 설정
prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

# GPT 모델 설정
gpt = GPT()
GLO_LOCK = False

# 토큰을 파일에서 불러옴
with open("./token_discord", "r") as fp:
    TOKEN = fp.readline()


async def gpt_request(message: discord.Message):
    try:
        async with message.channel.typing():
            result = await asyncio.to_thread(gpt.glo_request, message.content)
            _message = await message.reply(result)
    except:
        logger.exception("GPT 모델 호출 중 오류 발생")


async def gpt_stream(message: discord.Message):
    logger.info(f"name: {message.author.nick} - request: {message.content}")
    msg: discord.Message = None
    try:
        # 초기값 설정
        text = ""
        now = time.time()

        async with message.channel.typing():
            # GPT-3에 대한 요청
            async for r in gpt.stream_request(message.content):
                text += r
                if len(text) > 3:
                    try:
                        # 메시지를 일정 간격으로 업데이트
                        if time.time() - now > 1:
                            # 초기 응답 메시지가 없는 경우
                            if not msg or not msg.content:
                                now = time.time()
                                msg = await message.reply(text)
                            # 초기 응답 메시지가 있는 경우
                            else:
                                now = time.time()
                                await msg.edit(content=text)
                    except discord.errors.HTTPException:
                        logger.exception("전송 중 오류 발생")
                        logger.exception(text)

            # 최종 응답 메시지 업데이트
            await msg.edit(content=text)

    except:
        # 오류 발생 시 로그 기록
        logger.exception("GPT STREAM 호출 중 오류 발생")


@bot.event
async def on_ready():
    # 봇이 온라인으로 변경됨
    game = discord.Game("대화에 집중 ")
    await bot.change_presence(status=discord.Status.online, activity=game)
    logger.info("스타또~")


@bot.event
async def on_message(message: discord.Message):
    global GLO_LOCK

    # 봇이 메시지를 보낸 경우 어떠한 작업도 하지 않음.
    if message.author.bot:
        return

    if message.content.startswith(prefix):
        await bot.process_commands(message)
        return

    # GPT 채팅방인 경우 GPT 모델에게 메시지 전달
    if "gpt" in message.channel.name:
        await gpt_stream(message)


@bot.command(name="ask")
async def adk(ctx: commands.Context, *, arg: str):
    ctx.message.content = arg
    await gpt_stream(ctx.message)


@bot.command(name="clear")
async def clear_history(ctx: discord.Message):
    # GPT 모델의 기억 삭제
    gpt.clear_history()
    await ctx.channel.send("기억이 초기화되었습니다.")
    return None


@bot.command(name="test")
async def test(ctx: discord.Message, *args):
    # 테스트 메시지 전송
    await ctx.channel.send("테스트 중입니다.")
    return None


@bot.command(name="config")
async def config(ctx: discord.Message):
    await ctx.channel.send(f"글로벌 설정\n```!gconfig [설정명] [설정값]```\n유저 설정\n```!uconfig [설정명] [설정값]```")
    return None


@bot.command(name="gconfig")
async def glo_config(ctx: discord.Message, *args):
    if not args:
        # 설정 정보를 출력하는 경우
        await ctx.channel.send(f"```{json.dumps(gpt.gloSetting, indent=2, ensure_ascii=False)}```")
    elif len(args) == 1:
        # 설정 정보 중 하나만 출력하는 경우
        key = args[0]
        if key not in gpt.gloSetting:
            await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
        else:
            value = gpt.gloSetting[key]
            await ctx.channel.send(f"```{json.dumps(value, indent=2, ensure_ascii=False)}```")
    elif len(args) == 2:
        # 설정 정보를 변경하는 경우
        key, value = args[0], args[1]
        if key not in gpt.gloSetting:
            await ctx.channel.send(f"'{key}'이라는 설정은 존재하지 않습니다.")
        else:
            gpt.gloSetting[key] = value
            gpt.load_setting()
            await ctx.channel.send(f"```{key}: {value}```")
    else:
        await ctx.channel.send("```!gconfig [설정명] [설정값]``` 형태로 입력해주세요.")
        return None


@bot.command(name="role")
async def role_config(ctx: commands.Context, *args):
    try:
        if not args:
            # 역할 정보 초기화
            gpt.set_system_text("")
            await ctx.channel.send("역할 정보가 초기화되었습니다.")
            return None
        else:
            # 역할 정보 설정
            role_description = " ".join(args)
            gpt.set_system_text(role_description)
            await ctx.channel.send("역할 정보가 설정되었습니다.")
    except:
        logger.exception("역할 설정 중 오류 발생")
        return None

bot.run(TOKEN)

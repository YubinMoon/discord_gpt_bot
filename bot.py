from discord.ext import commands
import discord
from gpt import GPT
import json
import asyncio
import logging


# 로그 파일 경로 설정
LOG_FILENAME = 'log.log'

# 로그 레벨 설정
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H%M%S", encoding="utf-8", format="%(asctime)s - %(levelname)s \t %(name)s[%(funcName)s:%(lineno)d] - %(message)s")
logger = logging.getLogger(__name__)
prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)
gpt = GPT()
GLO_LOCK = False


with open("./token_discord", "r")as fp:
    TOKEN = fp.readline()


@bot.event
async def on_ready():
    # 'comment'라는 게임 중으로 설정합니다.
    game = discord.Game("대화에 집중 ")
    await bot.change_presence(status=discord.Status.online, activity=game)
    logger.info("스타또~")


@bot.event
async def on_message(message: discord.Message):
    global GLO_LOCK
    # 봇이 메시지를 보낸 경우 어떠한 작업도 하지 않음.
    if message.author.bot:
        return None
    # Commands 이벤트 진행
    await bot.process_commands(message)
    content = message.content
    if (content[0] == prefix):
        return None
    if ("gpt" in message.channel.name):
        try:
            async with message.channel.typing():
                result = await asyncio.to_thread(gpt.gloRequest, content)
                await message.reply(result)
        except:
            logger.exception("gpt")


@bot.command(name="clear")
async def clearHistory(ctx: discord.Message):
    # 기억 삭제
    await gpt.clearHistory()
    await ctx.channel.send("제 기억이 조기화 되었어요!")
    return None


@bot.command(name="test")
async def test(ctx: discord.Message, *args):
    # 유저가 요청했던 채널로 전송합니다.
    print(ctx)
    print(ctx.channel)
    await ctx.channel.send("테스트 중이에요!")
    return None


@bot.command(name="config")
async def config(ctx: discord.Message):
    await ctx.channel.send(f"글로벌 설정\n```!gconfig [설정명] [설정값]```\n유저 설정\n```!uconfig [설정명] [설정값]```")
    return None


@bot.command(name="gconfig")
async def config(ctx: discord.Message, *args):
    if (len(args) == 0):
        await ctx.channel.send(f"```{json.dumps(gpt.gloSetting, indent=2, ensure_ascii=False)}```")
        return None
    if (args[0] not in gpt.gloSetting):
        await ctx.channel.send(f"'{args[0]}'이라는 설정은 존재하지 않아요!")
        return None
    if (len(args) == 1):
        await ctx.channel.send(f"```{json.dumps(gpt.gloSetting[args[0]], indent=2, ensure_ascii=False)}```")
    elif (len(args) == 2):
        pass
    else:
        await ctx.channel.send("```!gconfig [설정명] [설정값]```\n으로 쓰셔야 해요!")
    return None


@bot.command(name="role")
async def role(ctx: discord.Message, *args):
    try:
        if (len(args) == 0):
            gpt.setSetting("")
            await ctx.channel.send(f"```!role [역할 설명]```\n으로 쓰셔야 해요!\n역할이 초기화 되었어요!")
            return None
        gpt.setSetting(" ".join(s for s in args))
        await ctx.channel.send("역할이 설정 되었어요!")
    except:
        logger.exception("role")
        return None


bot.run(TOKEN)

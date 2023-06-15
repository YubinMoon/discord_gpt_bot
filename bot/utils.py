import logging
import traceback
import discord
import json
from discord.ext import commands
from discord.errors import HTTPException
from discord_setting import gpt_container
from GPT import GPT

logger = logging.getLogger(__name__)


class UnValidCommandError(Exception):
    ...


class GPTHandler:
    def __init__(self, discord_message: discord.Message):
        self.discord_message: discord.Message = discord_message
        self.gpt: GPT = gpt_container.get_gpt(discord_message.channel.id)

    async def run(self):
        raise NotImplementedError

    async def reply(self, *args) -> discord.Message:
        return await self.discord_message.reply(*args)


class HandleErrors:
    def __init__(self, error_message: str):
        self.error_message = error_message

    def __call__(self, func):
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except NameError:
                logger.exception(traceback.format_exc())
                await self.send_error_message(*args)
            except HTTPException:
                logger.exception("응답 전송 중 오류 발생")
                await self.send_error_message(*args)
            except UnValidCommandError as e:
                logger.exception("커멘드 오류 발생")
                await self.send_error_message(*args, error_message=e)
            except:
                logger.exception(traceback.format_exc())

        return inner

    async def send_error_message(self, *args, error_message: str | None = None) -> None:
        message = error_message or self.error_message
        for arg in args:
            if isinstance(arg, (discord.Message, commands.context.Context, GPTHandler)):
                await arg.reply(message)
                break


def data_to_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)

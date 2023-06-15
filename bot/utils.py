import logging
import traceback
import discord
from discord.ext import commands
from discord.errors import HTTPException

logger = logging.getLogger(__name__)


class UnValidCommandError(Exception):
    ...


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
            if isinstance(arg, (discord.Message, commands.context.Context)):
                await arg.reply(message)
                break

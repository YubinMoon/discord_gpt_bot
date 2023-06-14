import logging
import traceback
import discord
from discord.errors import HTTPException

logger = logging.getLogger(__name__)


def handle_errors(error_message):
    def real_decorator(coro):
        async def wrapper(*args, **kwargs):
            try:
                return await coro(*args, **kwargs)
            except NameError:
                logger.exception(traceback.format_exc())
                await args[0].channel.send("GPT가 준비 중 이에요!")
            except HTTPException:
                logger.exception("응답 전송 중 오류 발생")
                for arg in args:
                    if isinstance(arg, discord.Message):
                        await arg.channel.send(error_message)
                        break
            except:
                logger.exception(traceback.format_exc())

        return wrapper

    return real_decorator

import logging
import os
from discord_setting import bot
from bot import command

LOG_FILENAME = "log.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s \t %(name)s[%(funcName)s:%(lineno)d] - %(message)s",
)
logger = logging.getLogger(__name__)
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)

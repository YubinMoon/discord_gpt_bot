import logging
import os
from bot.command import bot

LOG_FILENAME = "log.log"


class CustomFormatter(logging.Formatter):
    blue = "\x1b[36;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "[%(asctime)s] [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s"
    )

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def set_root_logger():
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s"
    )
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    console_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(LOG_FILENAME, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def main():
    set_root_logger()

    TOKEN = os.environ.get("DISCORD_TOKEN")
    bot.run(TOKEN)


if __name__ == "__main__":
    main()

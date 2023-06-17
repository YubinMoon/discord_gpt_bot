import logging
import time
import discord
import os
from .utils import HandleErrors, data_to_json, UnValidCommandError, GPTHandler

logger = logging.getLogger(__name__)
MAX_TEXT_LENGTH = 1900


class ChatHandler(GPTHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)
        self.text: str = ""
        self.now: int = 0
        self.msg: discord.Message

    @HandleErrors("GPT가 혀를 깨물었어요!")
    async def run(self):
        self.msg = await self.discord_message.reply("대답 중...")
        logger.info(
            f"name: {self.discord_message.author.nick} - request: {self.discord_message.content}"
        )
        await self.get_from_gpt_and_send_by_word()

        if 1 < len(self.text) < MAX_TEXT_LENGTH:
            await self.msg.edit(content=self.text)
        if MAX_TEXT_LENGTH <= len(self.text):
            await self.send_to_file()
            await self.msg.edit(content="")

    async def get_from_gpt_and_send_by_word(self):
        async for message in self.gpt.get_stream_chat(self.discord_message.content):
            self.text = message.content
            await self.send_after_timer()

    async def send_after_timer(self):
        if time.time() - self.now > 1:
            await self.send_by_word()

    async def send_by_word(self):
        self.now = time.time()
        if 1 < len(self.text) < MAX_TEXT_LENGTH:
            await self.msg.edit(content=self.text)
        elif MAX_TEXT_LENGTH <= len(self.text):
            await self.msg.edit(content=self.text[:MAX_TEXT_LENGTH] + "...")

    async def send_to_file(self):
        file_name = await self.gpt.short_chat(
            f"'{self.discord_message.content}' I need a file name to save the following question in a file. Please suggest an English file name within 10 characters. The file extension should be .txt!",
            "I am an AI that generates file names summarizing the content.",
        )
        if ".txt" not in file_name:
            file_name += ".txt"
        file_path = "temp/" + file_name
        if not os.path.isdir("temp"):
            os.mkdir("temp")
        logger.info(f"make file: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.text.replace(". ", ".\n"))
        await self.msg.add_files(discord.File(file_path, filename=file_name))


class ImageHandler(GPTHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)

    @HandleErrors("GPT가 손을 삐끗했어요!")
    async def run(self, *args: tuple[str]):
        prompt = " ".join(args)
        if not prompt:
            await self.reply("```!img [prompt]``` 형태로 입력해주세요.")
            return
        file_name = await self.gpt.short_chat(
            f"'{prompt}' I'm trying to generate and save an image with the following sentence, but I can't come up with a file name. Can you generate a file name in English within 10 characters. The file extension should be .png!",
            "I am an AI that generates file names summarizing the content.",
        )
        msg = await self.reply("생성 중...")
        data = await self.gpt.create_image(prompt=prompt)
        file = discord.File(data, filename=file_name)
        await msg.edit(content="생성 완료")
        await msg.add_files(file)


class ConfigHandler(GPTHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)

    @HandleErrors("설정을 불러오다 에러가 발생했어요!")
    async def run(self, *args: tuple[str]):
        if not args:
            setting = self.get_all_setting()
            await self.discord_message.reply(f"```{setting}```")
        elif len(args) == 1:
            setting = self.get_setting(key=args[0])
            await self.discord_message.reply(f"```{setting}```")
        elif len(args) == 2:
            key, value = args[0], " ".join(args[1:])
            await self.set_setting_and_reply(key, value)
        else:
            await self.discord_message.reply("```!gconfig [설정명] [설정값]``` 형태로 입력해주세요.")

    def get_all_setting(self):
        data = self.gpt.setting.setting_value
        return data_to_json(data)

    def get_setting(self, key: str) -> str:
        data = self.gpt.setting.setting_value
        if key not in data:
            raise UnValidCommandError(f"'{key}'이라는 설정을 찾을 수 없습니다.")
        else:
            return data_to_json(data[key])

    async def set_setting_and_reply(self, key: str, value: str) -> None:
        data = self.gpt.setting.setting_value
        if key not in data:
            raise UnValidCommandError(f"'{key}'이라는 설정을 찾을 수 없습니다.")
        else:
            self.gpt.setting.set_setting(key, value)
            new_value = self.gpt.setting.setting_value[key]
            await self.discord_message.reply(f"```{key}: {new_value}```")


class RoleHandler(GPTHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)

    @HandleErrors("역할을 설정하다 에러가 발생했어요!")
    async def run(self, *args: tuple[str]):
        if not args:
            await self.set_system_text_and_reply("")
        else:
            role_text = " ".join(args)
            await self.set_system_text_and_reply(role_text)

    async def set_system_text_and_reply(self, role_text: str = ""):
        self.gpt.setting.set_setting("system_text", role_text)
        await self.discord_message.reply("역할 정보가 변경되었어요.")


class HistoryHandler(GPTHandler):
    def __init__(self, discord_message: discord.Message):
        super().__init__(discord_message)

    @HandleErrors("기록을 탐색하다 에러가 발생했어요!")
    async def run(self, *args: tuple[str]):
        if not args:
            await self.show_history_and_reply()
        elif args[0] == "clear":
            await self.clear_history_and_reply()
        else:
            await self.discord_message.reply("```!history (clear)``` 형태로 입력해주세요.")

    async def show_history_and_reply(self):
        if self.gpt.message_box:
            await self.reply(
                f"```{data_to_json(self.gpt.message_box.make_messages())}```\n`!history clear` 로 초기화 할 수 있어요!"
            )
        else:
            await self.reply("기록이 없어요. \n대화를 시작해 볼까요?")

    async def clear_history_and_reply(self):
        if self.gpt.message_box:
            self.gpt.message_box.clear()
            await self.reply("기억을 초기화 했어요.")
        else:
            await self.reply("기록이 없어요. \n대화를 시작해 볼까요?")

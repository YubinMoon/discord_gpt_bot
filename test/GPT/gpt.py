import os
from unittest import IsolatedAsyncioTestCase
from GPT import gpt
from GPT.message import BaseMessage, AssistanceMessage
from dotenv import load_dotenv

load_dotenv()


class GptTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]

    async def test_stream_chat(self):
        chat = gpt.GPT(api_key=self.api_key)
        message = AssistanceMessage()
        async for msg in chat.get_stream_chat("안녕?"):
            message += msg
        self.assertGreater(len(message.content), 0)

    async def test_short_chat(self):
        chat = gpt.GPT(api_key=self.api_key)
        result = await chat.short_chat("안녕?", "당신은 친절한 AI 입니다.")
        self.assertGreater(len(result), 0)

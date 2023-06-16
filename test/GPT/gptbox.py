import os
from unittest import IsolatedAsyncioTestCase
from GPT import gptbox
from dotenv import load_dotenv

load_dotenv()


class GptboxTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]

    async def test_get_gpt(self):
        gpt_container = gptbox.GPTBox(self.api_key)
        gpt_list = set()
        for i in range(10):
            temp_gpt = gpt_container.get_gpt(i)
            gpt_list.add(temp_gpt)
        for i in range(10):
            temp_gpt = gpt_container.get_gpt(i)
            gpt_list.add(temp_gpt)
        self.assertEqual(len(gpt_list), 10)

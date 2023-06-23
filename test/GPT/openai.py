import os
from unittest import TestCase, IsolatedAsyncioTestCase
from GPT.openai import OpenaiApiClient, OpenaiApiStreamClient
from GPT import message
from dotenv import load_dotenv

load_dotenv()


def make_dummy_data(message: list):
    return {
        "model": "gpt-3.5-turbo",
        "messages": message,
        "temperature": 1.0,
        "top_p": 1.0,
    }


class OpenaiTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.usr_content1 = "안녕? "
        self.usr_msg1 = message.UserMessage(content=self.usr_content1)

    async def test_chat_client(self):
        chat_client = OpenaiApiClient(api_key=self.api_key)
        data = [self.usr_msg1.make_message()]
        response = await chat_client.get_request(data=make_dummy_data(data))
        print(response.json())

from GPT import openai
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.requestor
def test_chat_completion_create():
    result = openai.ChatCompletion.create()

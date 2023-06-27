from openai import ChatCompletion
from dotenv import load_dotenv
import pytest

load_dotenv()


@pytest.mark.requestor
def test_chat_completion_create():
    result = ChatCompletion.create()
    assert result is not None

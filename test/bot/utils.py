import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock, mock_open, patch
from bot import gpt_control
from discord import Message
from GPT.message import MessageLine


class GptControlTests(IsolatedAsyncioTestCase):  # TODO HandleErrors 디버깅
    pass

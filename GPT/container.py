from .chat import Chat, ChatStream, ChatStreamFunction
from .openai import ChatCompletion, ChatStreamCompletion
from .client import Client
from .interface import BaseContainer


class GPTContainer(BaseContainer):
    def __init__(self, api_key):
        self.api_key = api_key
        self.Client_container = {}

    def get_gpt_client(self, key: int | str) -> Client:
        if key in self.Client_container:
            return self.Client_container[key]
        else:
            self.Client_container[key] = Client(self)
            return self.Client_container[key]

    def get_gpt_chat(self, type: str) -> Chat:
        if type == "completion":
            openai_api = ChatCompletion()
            return Chat(self.api_key, openai_api)
        elif type == "stream":
            openai_api = ChatStreamCompletion()
            return ChatStream(self.api_key, openai_api)
        elif type == "stream_function":
            openai_api = ChatStreamCompletion()
            return ChatStreamFunction(self.api_key, openai_api)
        else:
            raise ValueError(
                "Invalid type. Valid types are: completion, stream, stream_function"
            )

    def __str__(self) -> str:
        return f"< ClientBox : {self.Client_container.keys()} >"

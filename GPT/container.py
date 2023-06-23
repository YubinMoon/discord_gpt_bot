from .chat import Chat, ChatStream, ChatStreamFunction
from .openai import ChatCompletion, ChatStreamCompletion


class Container:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_gpt_chat(self, type: str) -> Chat:
        raise NotImplementedError


class GPTContainer(Container):
    def __init__(self, api_key):
        self.api_key = api_key

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

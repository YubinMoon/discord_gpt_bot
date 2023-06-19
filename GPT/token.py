import tiktoken


class Tokener:
    encoding: tiktoken.Encoding

    @classmethod
    def num_tokens_from_messages(
        self, messages: list, model: str = "gpt-3.5-turbo-0613"
    ) -> int:
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        # 이전 메시지 리스트에서 사용된 토큰 수를 계산합니다.
        num_tokens = 0
        for message in messages:
            num_tokens += self.num_tokens_of_message(message)
        num_tokens += 2  # 답변은 <im_start>assistant로 시작함
        return num_tokens

    @classmethod
    def num_tokens_of_message(self, message: dict) -> int:
        num_tokens = 4  # <im_start>, role/name, \n, content, <im_end>, \n
        for key, value in message.items():
            value = str(value)
            num_tokens += self.num_tokens_of_key_and_value(key, value)
        return num_tokens

    @classmethod
    def num_tokens_of_key_and_value(self, key: str, value: str) -> int:
        num_tokens = len(self.encoding.encode(value))
        if key == "name":  # 이름이 있는 경우, 역할은 필요하지 않음
            num_tokens += -1  # 역할은 항상 필요하며, 1개의 토큰을 차지함
        return num_tokens

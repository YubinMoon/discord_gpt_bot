import openai
import openai.error
import json
import time
import logging
import tiktoken
import os


class GPT:
    def __init__(self):
        self.init_logger()
        self.lastRequestTime = time.time()
        openai.api_key_path = "api_openai"
        if os.path.isfile("setting.json"):
            self.gloSetting = json.load(
                open("setting.json", "r", encoding="utf-8"))
        else:
            self.create_global_settings()

    def init_logger(self):
        self.logger = logging.getLogger(__name__)
        fileHeader = logging.FileHandler("request.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        fileHeader.setFormatter(formatter)

    def create_global_settings(self):
        self.gloSetting = {
            "system_text": "",
            "history": [],
            "max_token": 2000,
            "disable_system": False,
            "show_question": False
        }
        json.dump(self.gloSetting, open(
            "setting.json", "w", encoding="utf-8"), indent=4)

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        """
        이전 메시지 리스트에서 사용된 토큰 수를 계산하여 반환합니다.

        Parameters:
            messages (list): 이전 메시지 리스트
            model (str, optional): 사용할 모델 (기본값: "gpt-3.5-turbo-0301")

        Returns:
            num_tokens (int): 이전 메시지 리스트에서 사용된 토큰 수
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        if model == "gpt-3.5-turbo-0301":
            # 이전 메시지 리스트에서 사용된 토큰 수를 계산합니다.
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # <im_start>, role/name, \n, content, <im_end>, \n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # 이름이 있는 경우, 역할은 필요하지 않음
                        num_tokens += -1  # 역할은 항상 필요하며, 1개의 토큰을 차지함
            num_tokens += 2  # 답변은 <im_start>assistant로 시작함

            return num_tokens
        else:
            raise NotImplementedError("그런 모델은 없어요")

    def make_new_messages(self, new_message_text: str, system_text: str, past_messages: list):
        """
        새 메시지를 생성하여 반환합니다.

        Parameters:
            new_message_text (str): 사용자가 입력한 메시지
            system_text (str): 시스템이 추가적으로 제공하는 메시지
            past_messages (list): 이전 메시지 리스트

        Returns:
            message (list): 생성된 메시지 리스트
        """
        system = {"role": "system", "content": system_text}
        new_message = {"role": "user", "content": new_message_text}

        # 시스템 메시지, 이전 메시지 리스트, 새 메시지를 조합하여 생성된 메시지 리스트를 반환합니다.
        message = [system] + (past_messages or []) + [new_message]
        return message

    def completion(self, new_message_text: str, system_text: str = "", past_messages: list = None):
        """
        OpenAI API를 사용하여 새 메시지를 생성하고 반환합니다.

        Parameters:
            new_message_text (str): 사용자가 입력한 메시지
            system_text (str, optional): 시스템이 추가적으로 제공하는 메시지 (기본값: "")
            past_messages (list, optional): 이전 메시지 리스트 (기본값: [])

        Returns:
            response (str): 생성된 답변 메시지
            past_messages (list): 토큰 수가 제한된 이전 메시지 리스트
        """
        # 이전 메시지 리스트에서 토큰 수를 제한합니다.
        past_messages = past_messages or []
        past_messages = self.control_token(past_messages)

        # 새 메시지를 생성합니다.
        message = self.make_new_messages(
            new_message_text, system_text, past_messages)

        # OpenAI API를 사용하여 답변을 생성합니다.
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )
        response = result.choices[0].message.content

        # 생성된 답변 메시지를 이전 메시지 리스트에 추가합니다.
        response_message = {"role": "assistant", "content": response}
        past_messages.append(response_message)

        # 토큰 수가 제한된 이전 메시지 리스트와 생성된 답변 메시지를 반환합니다.
        self.logger.info(past_messages)
        return response, past_messages

    def glo_request(self, message):
        """
        GLO 시스템에 요청을 보내고, 답변을 반환합니다.

        Parameters:
            message (str): 사용자가 입력한 메시지

        Returns:
            result (str): 생성된 답변 메시지
        """
        # 최근 요청 시간이 10분 이상 지났을 경우, 이전 메시지 리스트를 초기화합니다.
        if time.time() - self.lastRequestTime > 600:
            self.gloSetting["history"] = []
            self.lastRequestTime = time.time()

        # 이전 메시지 리스트를 가져옵니다.
        his = self.gloSetting["history"]

        # OpenAI API를 사용하여 답변을 생성하고, 이전 메시지 리스트를 업데이트합니다.
        setting = self.gloSetting["system_text"]
        result, his = self.completion(message, setting, his)
        self.gloSetting["history"] = his

        # 생성된 답변 메시지를 반환합니다.
        return result

    def control_token(self, past_messages=[]):
        """
        메시지의 토큰 수를 제한하고, 최대값을 초과하는 경우 이전 메시지를 제거합니다.

        Parameters:
            past_messages (list[str]): 이전 메시지 리스트

        Returns:
            past_messages (list[str]): 토큰 수가 제한된 이전 메시지 리스트
        """
        try:
            token = self.num_tokens_from_messages(past_messages)
            self.logger.info(f"token: {token}")

            # 토큰 수가 최대값을 초과하면, 최근 2개 이전의 메시지를 제거합니다.
            while token > self.gloSetting.get("max_token", 3000) and past_messages:
                past_messages = past_messages[2:]
                token = self.num_tokens_from_messages(past_messages)

            return past_messages
        except:
            self.logger.exception("Error in controlling past messages")

    async def clear_history(self):
        """
        채팅 기록을 초기화합니다.
        """
        self.logger.info("history cleared")
        self.gloSetting["history"] = []

    async def stream_completion(self, new_message_text: str, system_text: str = '', past_messages: list = []):
        # 현재 메시지와 이전 대화 내용을 합쳐서 새 메시지 리스트 생성
        messages = self.make_new_messages(
            new_message_text, system_text, past_messages)

        num_retries = 0
        while num_retries < 1:
            try:
                # OpenAI의 API를 사용해 새로운 메시지를 생성
                result = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    stream=True,
                    messages=messages
                )
            except openai.error.APIConnectionError:
                self.logger.exception("APIConnectionError 발생")
                num_retries += 1
                continue
            else:
                break
        else:
            self.logger.error("API 연결에 실패하여 종료합니다.")
            return
        # 대화 내용을 담을 리스트 생성
        collected_messages = []

        # 생성된 메시지를 루프 돌며 처리
        for chunk in result:
            # 생성된 메시지의 내용을 가져와서 저장
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            # 처리된 메시지를 리스트에 추가하고 반환
            yield chunk_message
            collected_messages.append(chunk_message)

        # 전체 대화 내용을 생성
        full_reply_content = ''.join([m for m in collected_messages])

        # 대화 내용 리스트에 새로운 대화 내용을 추가하고 토큰 수를 제어
        past_messages.append(
            {"role": "assistant", "content": full_reply_content})
        past_messages = self.control_token(past_messages)
        # 대화 내용 리스트를 저장
        self.logger.info(past_messages)
        self.gloSetting["history"] = past_messages
        return

    async def stream_request(self, message):
        # 10분에 한 번 새로운 채팅 세션을 시작한다.
        if time.time() - self.lastRequestTime > 600:
            self.gloSetting["history"] = []
            self.lastRequestTime = time.time()

        # 이전 메시지들과 설정 값을 가져온다.
        setting = self.gloSetting["system_text"]
        past_messages = self.gloSetting["history"]

        # stream_completion() 메서드를 통해 실시간 채팅을 진행하며, 결과를 yield로 반환한다.
        async for result in self.stream_completion(message, setting, past_messages):
            yield result

    def set_system_text(self, setting):
        self.gloSetting["system_text"] = setting

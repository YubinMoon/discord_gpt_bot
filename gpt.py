import openai
import openai.error
import json
import time
import logging
import tiktoken
import os
import asyncio


class GPT:
    def __init__(self, setting: str = "setting.json"):
        self.setting_file = setting
        self.gloSetting = {}
        self.logger = logging.getLogger(__name__)
        self.lastRequestTime = time.time()
        openai.api_key_path = "api_openai"
        self.load_setting()

    def load_setting(self):
        if not self.gloSetting and os.path.isfile(self.setting_file):
            self.gloSetting = json.load(
                open(self.setting_file, "r", encoding="utf-8"))
        self.model = self.gloSetting.get("model", "gpt-4-0314")
        self.system_text = self.gloSetting.get("system_text", "")
        self.max_token = self.gloSetting.get("max_token", "2000")
        self.temperature = self.gloSetting.get("temperature", "1")
        self.top_p = self.gloSetting.get("top_p", "1")
        self.keep_min = self.gloSetting.get("keep_min", "10")
        self.gloSetting = {
            "model": self.model,
            "system_text": self.system_text,
            "max_token": self.max_token,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "keep_min": self.keep_min,
        }
        self.clear_history()

        json.dump(self.gloSetting, open(
            self.setting_file, "w", encoding="utf-8"), indent=4)

        self.max_token = int(self.max_token)
        self.temperature = float(self.temperature)
        self.top_p = float(self.top_p)
        self.keep_min = int(self.keep_min)

    def make_line(self, content: str, role: str = "user"):
        return {"role": role, "content": content}

    def is_timeout(self):
        # 최근 요청 시간이 10분 이상 지났을 경우, 이전 메시지 리스트를 초기화합니다.
        if time.time() - self.lastRequestTime > self.keep_min*60:
            self.clear_history()
        self.lastRequestTime = time.time()

    def num_tokens_from_messages(self, messages: list):
        """
        이전 메시지 리스트에서 사용된 토큰 수를 계산하여 반환합니다.

        Parameters:
            messages (list): 이전 메시지 리스트
            model (str, optional): 사용할 모델 (기본값: "gpt-3.5-turbo-0301")

        Returns:
            num_tokens (int): 이전 메시지 리스트에서 사용된 토큰 수
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

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

    def control_token(self):
        """
        메시지의 토큰 수를 제한하고, 최대값을 초과하는 경우 이전 메시지를 제거합니다.

        Parameters:
            past_messages (list[str]): 이전 메시지 리스트

        Returns: None
        """
        try:
            token = self.num_tokens_from_messages(self.history)

            self.logger.info(f"use token: {token}")
            # 토큰 수가 최대값을 초과하면, 최근 2개 이전의 메시지를 제거합니다.
            while token > self.max_token and past_messages:
                past_messages = past_messages[2:]
                token = self.num_tokens_from_messages(past_messages)
        except:
            self.logger.exception("Error in controlling past messages")

    def make_new_messages(self, new_message_text: str, system_text: str, _past_messages: list = []):
        """
        새 메시지를 생성하여 반환합니다.

        Parameters:
            new_message_text (str): 사용자가 입력한 메시지
            system_text (str): 시스템이 추가적으로 제공하는 메시지
            _past_messages (list): 이전 메시지 리스트

        Returns:
            message (list): 생성된 메시지 리스트
        """
        message = []
        if self.system_text:
            message.append(self.make_line(role="system", content=system_text))
        new_message = self.make_line(content=new_message_text)

        # 시스템 메시지, 이전 메시지 리스트, 새 메시지를 조합하여 생성된 메시지 리스트를 반환합니다.
        message = message + _past_messages + [new_message]

        return message

    def completion(self, message: list):
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

        # OpenAI API를 사용하여 답변을 생성합니다.
        result = openai.ChatCompletion.create(
            model=self.model,
            messages=message,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        response = result.choices[0].message.content

        return response

    def glo_request(self, _message):
        """
        GLO 시스템에 요청을 보내고, 답변을 반환합니다.

        Parameters:
            _message (str): 사용자가 입력한 메시지

        Returns:
            result (str): 생성된 답변 메시지
        """
        self.is_timeout()

        # 새 메시지를 생성합니다.
        messages = self.make_new_messages(
            _message, self.system_text, self.history)

        # API 호출
        self.logger.info(f"message: {messages}")
        result = self.completion(messages)

        # 기록에 반영
        self.history.append(self.make_line(role="user", content=_message))
        self.history.append(self.make_line(role="assistant", content=result))

        # 기록에서 토큰 수를 제한합니다.
        self.control_token()

        # 생성된 답변 메시지를 반환합니다.
        return result

    async def stream_completion(self, messages: list):
        try:
            # OpenAI의 API를 사용해 새로운 메시지를 생성
            result = openai.ChatCompletion.create(
                model=self.model,
                stream=True,
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p,
            )
        except openai.error.APIConnectionError:
            yield "API 연결 실패"
            self.logger.exception(f"APIConnectionError 발생")
        except openai.error.RateLimitError:
            yield "API 과부하"
            self.logger.exception(f"RateLimitError 발생")
        except openai.error.InvalidRequestError:
            yield "설정 오류"
            self.logger.exception(f"InvalidRequestError 발생")
        except:
            yield "API 에러"
            self.logger.exception("API ERROR")
            raise openai.error.APIConnectionError("연결 실페~")

        # 생성된 메시지를 루프 돌며 처리
        for chunk in result:
            # 생성된 메시지의 내용을 가져와서 저장
            chunk_message = chunk['choices'][0]['delta'].get("content", "")
            # 처리된 메시지를 리스트에 추가하고 반환
            yield chunk_message
        return

    async def stream_request(self, _message):
        self.is_timeout()

        # 현재 메시지와 이전 대화 내용을 합쳐서 새 메시지 리스트 생성
        messages = self.make_new_messages(
            _message, self.system_text, self.history)

        # 대화 내용을 담을 리스트 생성
        collected_messages = []

        # stream_completion() 메서드를 통해 실시간 채팅을 진행하며, 결과를 yield로 반환한다.
        self.logger.info(f"message: {messages}")
        async for result in self.stream_completion(messages):
            collected_messages.append(result)
            yield result

        # 전체 대화 내용을 생성
        full_reply_content = ''.join([m for m in collected_messages])
        self.logger.info(f"request: {full_reply_content}")

        # 기록에 반영
        self.history.append(self.make_line(role="user", content=_message))
        self.history.append(self.make_line(
            role="assistant", content=full_reply_content))

        # 기록에서 토큰 수를 제한합니다.
        self.control_token()

    def clear_history(self):
        """
        채팅 기록을 초기화합니다.
        """
        self.logger.info("history cleared")
        self.history = []

    def set_system_text(self, setting):
        self.system_text = setting
        self.save_setting()

    def set_temperature(self, temperature):
        self.temperature = temperature
        self.save_setting()

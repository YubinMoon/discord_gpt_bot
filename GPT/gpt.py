import openai.error
import json
import time
import logging
import tiktoken
import os
import asyncio
import aiohttp
import datetime
import io
from dotenv import load_dotenv
from .setting import Setting


class GPT:
    def __init__(self, api_key: str, setting_file: str = "setting.json"):
        self.setting = Setting(setting_file)
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.lastRequestTime = time.time()
        if not os.path.isdir("./img"):
            os.mkdir("img")
        self.clear_history()

    def num_tokens_from_messages(self, messages: list) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.setting.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        # 이전 메시지 리스트에서 사용된 토큰 수를 계산합니다.
        num_tokens = 0
        for message in messages:
            num_tokens += self.get_token_of_message(encoding, message)
        num_tokens += 2  # 답변은 <im_start>assistant로 시작함

        return num_tokens

    def get_token_of_message(self, encoding: tiktoken.Encoding, message: dict) -> int:
        num_tokens = 4  # <im_start>, role/name, \n, content, <im_end>, \n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # 이름이 있는 경우, 역할은 필요하지 않음
                num_tokens += -1  # 역할은 항상 필요하며, 1개의 토큰을 차지함
        return num_tokens

    def control_token(self):
        try:
            token = self.num_tokens_from_messages(self.history)

            self.logger.info(f"use token: {token}")
            # 토큰 수가 최대값을 초과하면, 최근 2개 이전의 메시지를 제거합니다.
            while token > self.setting.max_token and past_messages:
                past_messages = past_messages[2:]
                token = self.num_tokens_from_messages(past_messages)
        except:
            self.logger.exception("Error in controlling past messages")

    def make_messages(
        self, new_message_text: str, system_text: str, _past_messages: list = []
    ) -> list[dict[str, str]]:
        message = []
        if self.setting.system_text:
            message.append(
                self.make_line(role="system", content=self.setting.system_text)
            )
        new_message = self.make_line(content=new_message_text)
        message = message + _past_messages + [new_message]
        return message

    async def chat_completion(self, message: list):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.setting.model,
            "messages": message,
            "temperature": self.setting.temperature,
            "top_p": self.setting.top_p,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions", headers=headers, json=data
            ) as resp:
                result = await resp.json()
                response = result["choices"][0]["message"]["content"]
        return response

    async def chat_request(self, _message):
        self.is_timeout()

        messages = self.make_messages(_message, self.setting.system_text, self.history)

        self.logger.info(f"message: {messages}")
        result = await self.chat_completion(messages)

        self.history.append(self.make_line(role="user", content=_message))
        self.history.append(self.make_line(role="assistant", content=result))

        self.control_token()

        return result

    async def stream_chat_completion(self, messages: list):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": self.setting.model,
                "messages": messages,
                "temperature": self.setting.temperature,
                "top_p": self.setting.top_p,
                "stream": True,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                ) as response:
                    # 스트림의 응답을 처리합니다.
                    async for chunk in response.content.iter_chunks():
                        # 두 줄로 나눕니다.
                        response_data = chunk[0].decode("utf-8").split("\n\n")
                        for data in response_data:
                            if data.startswith("data: "):
                                data = data[6:]  # "data: "를 제거합니다.
                                # JSON을 딕셔너리로 변환합니다.
                                data_dict = json.loads(data)
                                # 출력이 끝나면 함수 종료
                                if data_dict["choices"][0]["finish_reason"] == "stop":
                                    return
                                # 생성된 메시지의 내용을 가져와서 저장
                                response = data_dict["choices"][0]["delta"].get(
                                    "content", ""
                                )
                                yield response

        except aiohttp.ClientConnectionError:
            yield "API 연결 실패"
        except aiohttp.ClientResponseError:
            yield "API 응답 오류"
        except Exception as e:
            yield "API 에러"
            import traceback

            logging.exception(traceback.print_exc())
            raise openai.error.APIConnectionError("연결 실패") from e

    async def stream_chat_request(self, _message):
        self.is_timeout()

        # 현재 메시지와 이전 대화 내용을 합쳐서 새 메시지 리스트 생성
        messages = self.make_messages(_message, self.setting.system_text, self.history)

        # 대화 내용을 담을 리스트 생성
        collected_messages = []

        # stream_completion() 메서드를 통해 실시간 채팅을 진행하며, 결과를 yield로 반환한다.
        self.logger.info(f"message: {messages}")
        async for result in self.stream_chat_completion(messages):
            collected_messages.append(result)
            yield result

        # 전체 대화 내용을 생성
        full_reply_content = "".join([m for m in collected_messages])
        self.logger.info(f"request: {full_reply_content}")

        # 기록에 반영
        self.history.append(self.make_line(role="user", content=_message))
        self.history.append(
            self.make_line(role="assistant", content=full_reply_content)
        )

        # 기록에서 토큰 수를 제한합니다.
        self.control_token()

    async def create_image(self, prompt: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        async with self.session.post(
            "https://api.openai.com/v1/images/generations", headers=headers, json=data
        ) as resp:
            if resp.status != 200:
                print(resp)
                raise Exception("API 요청 에러")
            result = await resp.json()
            url = result["data"][0]["url"]
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with open(
                    f"./img/{datetime.datetime.now().strftime('%m%d%H%M%S')}.png", "wb"
                ) as f:
                    f.write(data)
                image_data = io.BytesIO(data)
                return image_data
            else:
                raise Exception("이미지 다운 에러")

    def make_line(self, content: str, role: str = "user"):
        return {"role": role, "content": content}

    def clear_history(self):
        """
        채팅 기록을 초기화합니다.
        """
        self.logger.info("history cleared")
        self.history = []

    def set_system_text(self, setting):  # TODO 셋팅 변경 추가
        pass
        # self.system_text = setting
        # self.load_setting()

    def is_timeout(self):
        # 최근 요청 시간이 10분 이상 지났을 경우, 이전 메시지 리스트를 초기화합니다.
        if time.time() - self.lastRequestTime > self.setting.keep_min * 60:
            self.clear_history()
        self.lastRequestTime = time.time()

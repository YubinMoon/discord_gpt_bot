import openai
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


class GPT:
    def __init__(self, setting: str = "setting.json"):
        self.setting_file = setting
        self.gloSetting = {}
        self.logger = logging.getLogger(__name__)
        self.lastRequestTime = time.time()
        self.session = aiohttp.ClientSession()
        openai.api_key_path = "api_openai"
        self.load_setting()
        # 토큰을 파일에서 불러옴
        with open("./api_openai", "r") as fp:
            openai.api_key = fp.readline().strip()
        if not os.path.isdir("./img"):
            os.mkdir('img')

    def load_setting(self):
        default_settings = {
            "model": "gpt-4-0314",
            "system_text": "",
            "max_token": 2000,
            "temperature": 1.0,
            "top_p": 1.0,
            "keep_min": 10,
        }
        if os.path.isfile(self.setting_file):
            with open(self.setting_file, "r", encoding="utf-8") as file:
                loaded_settings = json.load(file)
                self.gloSetting = {**default_settings, **loaded_settings}
        else:
            self.gloSetting = default_settings

        self.clear_history()
        self.save_setting()

    def save_setting(self):
        with open(self.setting_file, "w", encoding="utf-8") as file:
            json.dump(self.gloSetting, file, indent=4)

        self.model = self.gloSetting["model"]
        self.system_text = self.gloSetting["system_text"]
        self.max_token = int(self.gloSetting["max_token"])
        self.temperature = float(self.gloSetting["temperature"])
        self.top_p = float(self.gloSetting["top_p"])
        self.keep_min = int(self.gloSetting["keep_min"])

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

    async def chat_completion(self, message: list):
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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        }
        data = {
            "model": self.model,
            "messages": message,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }
        async with self.session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as resp:
            result = await resp.json()
            response = result["choices"][0]["message"]["content"]
        return response

    async def chat_request(self, _message):
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
        result = await self.chat_completion(messages)

        # 기록에 반영
        self.history.append(self.make_line(role="user", content=_message))
        self.history.append(self.make_line(role="assistant", content=result))

        # 기록에서 토큰 수를 제한합니다.
        self.control_token()

        # 생성된 답변 메시지를 반환합니다.
        return result

    async def stream_chat_completion(self, messages: list):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}"
            }
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True,
            }
            async with self.session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as response:
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
                                "content", "")
                            yield response

        except aiohttp.ClientConnectionError:
            yield "API 연결 실패"
        except aiohttp.ClientResponseError:
            yield "API 응답 오류"
        except Exception as e:
            yield "API 에러"
            raise openai.error.APIConnectionError("연결 실패") from e

    async def stream_chat_request(self, _message):
        self.is_timeout()

        # 현재 메시지와 이전 대화 내용을 합쳐서 새 메시지 리스트 생성
        messages = self.make_new_messages(
            _message, self.system_text, self.history)

        # 대화 내용을 담을 리스트 생성
        collected_messages = []

        # stream_completion() 메서드를 통해 실시간 채팅을 진행하며, 결과를 yield로 반환한다.
        self.logger.info(f"message: {messages}")
        async for result in self.stream_chat_completion(messages):
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

    async def create_image(self, prompt: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        async with self.session.post("https://api.openai.com/v1/images/generations", headers=headers, json=data) as resp:
            if resp.status != 200:
                print(resp)
                raise Exception("API 요청 에러")
            result = await resp.json()
            url = result["data"][0]["url"]
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with open(f"./img/{datetime.datetime.now().strftime('%m%d%H%M%S')}.png", "wb") as f:
                    f.write(data)
                image_data = io.BytesIO(data)
                return image_data
            else:
                raise Exception("이미지 다운 에러")

    def clear_history(self):
        """
        채팅 기록을 초기화합니다.
        """
        self.logger.info("history cleared")
        self.history = []

    def set_system_text(self, setting):
        self.system_text = setting
        self.load_setting()

# 사용 예시


async def main():
    gpt = GPT()
    data = await gpt.create_image("a blue eyes cat")
    with open("test.png", "wb") as f:
        f.write(data)

# main 함수를 실행하고 완료되면 이벤트 루프를 종료합니다.
if __name__ == "__main__":
    asyncio.run(main())

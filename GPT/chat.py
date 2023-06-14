import aiohttp
import logging
import json

from typing import Iterator, AsyncGenerator, AsyncIterator

logger = logging.getLogger(__name__)


async def stream_chat_request(headers: dict, data: dict) -> AsyncIterator[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
        ) as response:
            # 스트림의 응답을 처리합니다.
            # await process_stream_request(response=response)
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
                        response = data_dict["choices"][0]["delta"].get("content", "")
                        yield response


# async def process_stream_request(
#     response: aiohttp.ClientResponse,
# ) -> AsyncGenerator[str]:
#     print(response)

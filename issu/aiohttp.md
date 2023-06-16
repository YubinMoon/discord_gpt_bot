# ResourceWarning Debuging

aiohttp에서 ResourceWarning이 발생하는 이슈를 해결하기 위한 문서

## 라이브러리 이슈

[멘토님이 알려주신 이슈](https://github.com/aio-libs/aiohttp/issues/5277)

### 시도

4.0.0 버전에서 해결될 것으로 기대

```bash
pip install aiohttp==
```

버전 검색

```bash
pip install aiohttp==4.0.0a0
```

설치

### 결과

```bash
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
discord-py 2.2.2 requires aiohttp<4,>=3.7.4, but you have aiohttp 4.0.0a0 which is incompatible.
```

discord 패키지와 충돌

```bash
Traceback (most recent call last):
  File "C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\unittest\async_case.py", line 64, in _callTestMethod
    self._callMaybeAsync(method)
  File "C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\unittest\async_case.py", line 87, in _callMaybeAsync
    return self._asyncioTestLoop.run_until_complete(fut)
  File "C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 646, in run_until_complete
    return future.result()
  File "C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\unittest\async_case.py", line 101, in _asyncioLoopRunner
    ret = await awaitable
  File "C:\Users\TERRY\Desktop\workspace\bot\test\GPT\chat.py", line 40, in test_run5
    response = await chat_api.run(messages=self.messages, setting=self.setting)
  File "C:\Users\TERRY\Desktop\workspace\bot\GPT\chat.py", line 25, in run
    return await self.chat_request()
  File "C:\Users\TERRY\Desktop\workspace\bot\GPT\chat.py", line 29, in chat_request
    response = await session.post(
  File "C:\Users\TERRY\Desktop\workspace\bot\venv\lib\site-packages\aiohttp\client.py", line 463, in _request
    conn = await self._connector.connect(
  File "C:\Users\TERRY\Desktop\workspace\bot\venv\lib\site-packages\aiohttp\connector.py", line 522, in connect
    proto = await self._create_connection(req, traces, timeout)
  File "C:\Users\TERRY\Desktop\workspace\bot\venv\lib\site-packages\aiohttp\connector.py", line 853, in _create_connection
    _, proto = await self._create_direct_connection(
  File "C:\Users\TERRY\Desktop\workspace\bot\venv\lib\site-packages\aiohttp\connector.py", line 952, in _create_direct_connection
    hosts = await asyncio.shield(self._resolve_host(
TypeError: shield() got an unexpected keyword argument 'loop'
```

asyncio와 충돌

### 원인

[링크](https://docs.aiohttp.org/en/stable/)

>Note that the cchardet project is known not to support Python 3.10 or higher. See #6819 and GitHub: PyYoshi/cChardet/issues/77 for more details.

python 3.10 이상에선 충돌이 나나보다

## 코드 이슈

### 시도

```python
async with aiohttp.ClientSession() as session:
    async with session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=self.header,
        json=self.data,
    ) as response:
```

원래 stream을 사용하여 위와 같은 with을 사용하였는데 이게 문제일가 싶었음

```python
async with aiohttp.ClientSession() as session:
    response = await session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=self.header,
        json=self.data,
    )
```

위와 같이 변경

### 결과

```bash
...C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\traceback.py:363: ResourceWarning: unclosed <socket.socket fd=736, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('192.168.21.44', 51684), raddr=('104.18.6.192', 443)>
  fnames = set()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\asyncio\proactor_events.py:115: ResourceWarning: unclosed transport <_ProactorSocketTransport fd=-1 read=<_OverlappedFuture cancelled created at C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\asyncio\windows_events.py:493>>
  _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\traceback.py:363: ResourceWarning: unclosed <socket.socket fd=836, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('192.168.21.44', 51687), raddr=('104.18.6.192', 443)>
  fnames = set()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
C:\Users\TERRY\AppData\Local\Programs\Python\Python310\lib\traceback.py:363: ResourceWarning: unclosed <socket.socket fd=704, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('192.168.21.44', 51691), raddr=('104.18.6.192', 443)>
  fnames = set()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
```

경고가 나타나는 타이밍이 좀 늦어지긴 하였으나 여전히 경고 발생

### 원인

당연함 with 안에서 close() 를 해줄텐데 밖으로 뺀다고 달라지면 좀 실망스럽다

## 라이브러리 변경

GPT야 도와줘

>파이썬에서 request는 비동기 요청이나 http stream을 사용하지 못하는데 대안이 있을 까 3.10 버전을 사용하고 있어

>Python에서 가장 많이 사용되는 비동기 HTTP 클라이언트 라이브러리 중 하나는 httpx입니다. httpx는 Python 3.6 이상의 버전과 함께 사용할 수 있으며, 비동기 요청을 지원하고 HTTP 스트림을 처리할 수 있는 기능을 제공합니다.

### 시도

설치

```bash
pip install httpx
```

코드 변경

```python
async def chat_request(self) -> str:
    async with httpx.AsyncClient() as session:
        response = await session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self.header,
            json=self.data,
        )
        resp = response.json()
        if "error" in resp:
            raise ChatAPIError(resp.get("error"))
        return resp.get("choices")[0].get("message").get("content")
```

과연.....

```bash
(venv) PS C:\Users\TERRY\Desktop\workspace\bot> python test.py
안녕하세요! 무엇을 도와드릴까요?
.....
----------------------------------------------------------------------
Ran 5 tests in 5.473s

OK
```

성공!!!

## 결론

이상한 라이브러리 말고 유명한거 쓰자

추상화가 잘되어 있어 기존 코드와 충돌이 안난다. (클린코드 사랑해요)

GPT 최고!
# 디스코드 챗봇 - GPT 디스코드 봇

이 프로젝트는 디스코드 챗봇을 만들기 위한 파이썬 코드입니다. GPT-3.5-turbo 모델을 사용하여 자연스러운 대화를 생성합니다.


## 요구사항

- Python 3.10 이상
- `discord` 라이브러리
- `openai` 라이브러리

## 설치

1. `discord.py` 라이브러리 설치:

```
pip install discord.py
```

2. `openai` 라이브러리 설치:

```
pip install openai
```

3. 이 프로젝트의 루트 폴더에 `token_discord` 파일을 생성하고, 디스코드 봇 토큰을 추가합니다.

4. 이 프로젝트의 루트 폴더에 `api_openai` 파일을 생성하고, OpenAI API 키를 추가합니다.

## 사용 방법

1. 봇을 실행하기 위해 `bot.py` 파일을 실행합니다.

```
python bot.py
```


2. 디스코드 서버에 봇을 초대한 뒤, 봇과 대화할 수 있는 채널을 생성합니다. 이 채널의 이름에 'gpt'가 포함되어 있어야 합니다.

3. 봇이 온라인 상태가 되면, 채널에서 봇과 대화를 시작할 수 있습니다.

## 사용 가능한 명령어

- `!clear`: 봇의 대화 기록을 초기화합니다.
- `!test`: 봇이 "테스트 중이에요!"라는 메시지를 전송합니다.
- `!config`: 설정 메뉴를 표시합니다.
- `!gconfig`: 글로벌 설정을 조회하거나 변경합니다.
- `!role`: 봇의 역할을 설정하거나 초기화합니다.

## 파일 구조

- `bot.py`: 디스코드 봇의 주 실행 파일입니다.
- `gpt.py`: GPT-3.5-turbo 모델을 사용하여 대화를 생성하는 코드가 포함되어 있습니다.
- `log.log`: 실행 중 발생하는 로그를 기록합니다.
- `request.log`: GPT 요청에 대한 로그를 기록합니다.
- `user_setting.json`: 유저 설정을 저장하는 JSON 파일입니다 (없을 경우 자동 생성됩니다).
- `setting.json`: 전역 설정을 저장하는 JSON 파일입니다 (없을 경우 자동 생성됩니다).

## 설정

1. OpenAI API 키 발급: https://beta.openai.com/signup/ 에 접속하여 회원가입 후 API 키를 발급받습니다.

2. 디스코드 봇 토큰 발급: https://discord.com/developers/applications 에 접속하여 봇을 생성하고 토큰을 발급받습니다.

3. 발급받은 OpenAI API 키를 이 프로젝트의 루트 폴더에 `api_openai` 파일에 저장합니다.

4. 발급받은 디스코드 봇 토큰을 이 프로젝트의 루트 폴더에 `token_discord` 파일에 저장합니다.

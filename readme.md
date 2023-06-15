# DISCORD GPT CHAT BOT

디스코드에서 chat GPT를 간편하게 사용하기 위해 제작된 파이썬 디스코드 봇

## Environment

- Python 3.10.6

## Install

1. install python packages

    ```bash
    pip install -r requirements.txt
    ```

2. set .env file

    ```bash
    cp .env.template .env
    ```

3. set environment variables
    
    at the `.env` file,  
    [get openai api key](https://platform.openai.com/account/api-keys)  
    set your openai api key to `OPENAI_API_KEY`  

    [create discord bot](https://discord.com/developers/applications)  
    set your discord bot token to `DISCORD_TOKEN`  

## How to use

1. Invite the bot to your discord server

2. Create a text channel that contains the word 'gpt'

3. run the bot with the command below

    ```bash
    python main.py
    ```

4. start chatting with the bot in the channel

## Command List

- `!ask`: can chatting with gpt anywhere of server 

- `!config`: set/get the gpt config

- `!history`: show/clear the chat history

- `!ping`: pong!

- `!role`: set the system text of gpt bot

- `!img`: gpt make your own image with prompt

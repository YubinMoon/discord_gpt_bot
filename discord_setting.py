import os
import discord
from discord.ext import commands
from GPT import GPTBox
from dotenv import load_dotenv

load_dotenv()
bot_prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

gpt_container = GPTBox(os.environ["OPENAI_API_KEY"])

import os
import discord
from discord.ext import commands
from GPT import GPTBox

bot_prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

gpt_container = GPTBox(os.environ["OPENAI_API_KEY"])

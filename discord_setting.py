import os
import discord
from discord.ext import commands
from GPT import GPT

bot_prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

gpt = GPT(os.environ["OPENAI_API_KEY"])

# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands


intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f"Slaya ama ready")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def hello(ctx):
    await ctx.send("Choo choo! 🚅")


bot.run(os.environ["DISCORD_TOKEN"])

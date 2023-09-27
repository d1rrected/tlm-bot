# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands
import services.spreadsheet


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

@bot.command()
async def yoba(ctx):
    sheet = services.spreadsheet.SpreadSheet("objectives_list")
    value = sheet.cell(1, 1).value
    await ctx.send("yoba" + value)

bot.run(os.environ["DISCORD_TOKEN"])

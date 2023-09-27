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
    sheet = services.spreadsheet.SpreadSheet("objectives_list", "Upcoming Objectives")
    records_list = sheet.get_all_records()
    for record in records_list:
        if record["Type"]:
            await ctx.send(record["Type"])
        else:
            await ctx.send("Empty!")

    for record in records_list:
        if record:
            await ctx.send(record)

bot.run(os.environ["DISCORD_TOKEN"])

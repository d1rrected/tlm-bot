# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands, tasks
import services.spreadsheet
from datetime import datetime, timedelta
from discord.ext import commands
import logging

logging.basicConfig(level=logging.ERROR)
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
sheet = services.spreadsheet.SpreadSheet("objectives_list", "Upcoming Objectives")
records_in_memory = sheet.get_all_records()
time_utc_column_num = 3

OUTPUT_CHANNEL_NAME = "main"
dt_format = '%Y-%m-%d %H:%M:%S'

@bot.event
async def on_ready():
    update_output_channel.start()
    if not update_sheet.is_running():
        update_sheet.start()
    print(f"Slaya ama ready")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def hello(ctx):
    await ctx.send("Choo choo! 🚅")

@bot.command()
async def add(ctx, type_: str, map_: str, time_until: str):
    global records_in_memory

    try:
        # Convert the TIME_UNTIL into a timedelta
        hours, minutes = map(int, time_until.split(':'))
        delta = timedelta(hours=hours, minutes=minutes)

        # Calculate TIME_UTC
        current_time = datetime.utcnow()
        time_utc = current_time + delta

        # Format TIME_UTC into a string if needed
        time_utc_str = time_utc.strftime(dt_format)

        # Check if record already exists

        for record in records_in_memory:
            record_time = datetime.strptime(record['Time (UTC)'], dt_format)
            
            # If type, map, and time (±5 minutes) match, then don't add
            if record['Type'] == type_ and record['Map'] == map_ and \
            (record_time - timedelta(minutes=5)) <= time_utc <= (record_time + timedelta(minutes=5)):
                await ctx.send("Record with similar data already exists!")
                return

        # Prepare the row to be inserted
        row = [type_, map_, time_until, time_utc_str]

        # Find the correct position to insert
        rows = sheet.SHEET.get_all_values()
        insert_position = len(rows) + 1  # Assuming we insert at the end by default

        for idx, record_row in enumerate(rows[1:], start=2):  # Starting from 2 to skip the header
            record_time_utc_str = record_row[time_utc_column_num]  # Assuming 'Time (UTC)' is the 4th column
            record_time_utc = datetime.strptime(record_time_utc_str, dt_format)
            if time_utc < record_time_utc:
                insert_position = idx
                break

        # Inserting the new record at the found position
        sheet.SHEET.insert_row(row, insert_position)
        new_record = {'Type': row[0], 'Map': row[1], 'Time until (minutes)': row[2], 'Time (UTC)': row[3]}
        records_in_memory.append(new_record)
        await ctx.send(f"Added {type_} on {map_} with {time_until} left.")
    except Exception as e:
        logging.exception("Error in add.")

@tasks.loop(minutes=1)
async def update_sheet():
    try:
        records_in_memory = sheet.get_all_records()

        updated_rows = []
        for record in records_in_memory:
            event_time_utc = datetime.strptime(record['Time (UTC)'], '%Y-%m-%d %H:%M:%S')
            utc_now = datetime.utcnow()
            if event_time_utc > utc_now:
                # Assuming the record looks like: [TYPE, MAP, TIME_UNTIL, TIME_UTC]
                # Modify as needed
                time_diff = event_time_utc - utc_now
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                new_until_minutes = "{:02d}:{:02d}".format(hours, minutes)
                time_utc_str = event_time_utc.strftime(dt_format)
                updated_rows.append([record['Type'], record['Map'], new_until_minutes, time_utc_str])

        # Assuming data starts from row 2 (1 being header) and column 1 (A)
        # You might need to adjust based on where your data starts
        if updated_rows:
            range_name = f"A2:D{1 + len(updated_rows)}"
            sheet.clean_all_records()
            sheet.batch_update(range_name, updated_rows)
        else:
            sheet.clean_all_records()

    except Exception as e:
        logging.exception("Error in update_sheet")

@tasks.loop(minutes=1)
async def update_output_channel():
    # Get the output channel
    guild = bot.guilds[0]  # Assuming bot is in only one guild; adjust as needed
    output_channel = discord.utils.get(guild.text_channels, name=OUTPUT_CHANNEL_NAME)

    if not output_channel:
        print(f"Cannot find channel with name {OUTPUT_CHANNEL_NAME}")
        return

    # Fetch the latest messages to find the bot's message
    messages = [msg async for msg in output_channel.history(limit=10)]  # Retrieve the last 10 messages; adjust as needed
  # Retrieve the last 10 messages; adjust as needed
    bot_message = next((msg for msg in messages if msg.author == bot.user), None)

    # Get data from the spreadsheet
    data = sheet.SHEET.get_all_values()
    headers = data[0]
    rows = data[1:]

    # Convert the data to a table format
    table = "```"
    table += " | ".join(headers) + "\n"
    table += "-+-".join(["-"*len(header) for header in headers]) + "\n"  # separator line
    for row in rows:
        table += " | ".join(row) + "\n"
    table += "```"

    # Update the bot's message if it exists, else send a new one
    if bot_message:
        await bot_message.edit(content=table)
    else:
        await output_channel.send(content=table)

bot.run(os.environ["DISCORD_TOKEN"])

# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands, tasks
import services.spreadsheet
from datetime import datetime, timedelta
from discord import app_commands
import logging
from typing import List
import helper_functions
#from table2ascii import table2ascii as t2a, PresetStyle, Alignment

logging.basicConfig(level=logging.ERROR)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_ids=[700787012525097050, 375510056260861952])
#client = discord.Client(intents=intents)
#tree = app_commands.CommandTree(client)
#tree = app_commands.CommandTree(bot)
sheet = services.spreadsheet.SpreadSheet("objectives_list", "Upcoming Objectives")
records_in_memory = sheet.get_all_records()
time_utc_column_num = 3
all_zones = [
    'Sunstrand Shoal', 'Frostspring Vulcano', 'Frostspring Passage', 'Southgrove Thicket', 'Sunstrand Quicksands', 'Stonemouth Southbluff', 'Stonemouth Bay', 'Dryvein Steppe', 'Southgrove Copse', 'Sunstrand Dunes', 'Sunstrand Delta', 'Stonemouth Northbluff', 'Dryvein Confluence', 'Dryvein Cross', 'Dryvein End', 'Dryvein Oasis', 'Dryvein Plain', 'Dryvein Riverbed', 'Farshore Bay', 'Farshore Cape', 'Farshore Drylands', 'Farshore Esker', 'Farshore Heath', 'Farshore Lagoon'
]
all_objectives = [
    'Vortex', 'Castle', '7.4', '8.4', 'Core'
]
all_objective_levels = [
    'Green', 'Blue', 'Purple', 'Gold'
]

OUTPUT_CHANNEL_NAME = "output"
dt_format = '%Y-%m-%d %H:%M:%S'


def butify_dt_utc(datetime):
    date_obj = datetime.strptime(datetime, dt_format)
    return date_obj.strftime('%H:%M UTC')

def draw_table(data):
    if not data:
        return ""

    # Determine the maximum width for each column
    col_widths = [max(len(str(item)) for item in col) for col in zip(*data)]

    # Draw the table
    table = []
    for row in data:
        # Ensure each cell has the same width by padding with spaces as needed
        padded_row = [str(item).ljust(width) for item, width in zip(row, col_widths)]
        table.append("|   " + "   |   ".join(padded_row) + "   |   ")

    return "\n".join(table)

def transform_single_objective(objective_parameters):
    """Transforms a single list as per the given specifications."""
    def transform_string(objective):
        # Check and prepend/append appropriate emoji
        if "green" in objective.lower():
            return ":green_square: **" + objective + "** :green_square:"
        elif "purple" in objective.lower():
            return ":purple_square: **" + objective + "** :purple_square:"
        elif "blue" in objective.lower():
            return ":blue_square: **" + objective + "** :blue_square:"
        elif "gold" in objective.lower():
            return ":yelow_square: **" + objective + "** :yelow_square:"
        else:
            return objective

    # Apply the transformation to each element of the list (except the last one)
    transformed_data = [transform_string(objective) for objective in objective_parameters[:-1]]

    # Convert the last string to datetime and then format it as "HH:mm UTC"
    date_obj = datetime.strptime(objective_parameters[-1], '%Y-%m-%d %H:%M:%S')
    transformed_data.append(date_obj.strftime('%H:%M UTC'))
    
    # Add "In " before the third item
    transformed_data[2] = "In " + objective_parameters[2]
    
    return transformed_data

@bot.event
async def on_ready():
    await bot.tree.sync()
    update_output_channel.start()
    if not update_sheet.is_running():
        update_sheet.start()
    print(f"Slaya ama ready")

@bot.tree.command()
async def add(interaction: discord.Interaction, objective_level: str, objective: str, zone: str, hours: int, minutes: int):
    if zone not in all_zones:
        return
    if objective not in all_objectives:
        return
    if objective_level not in all_objective_levels:
        return
    
    if not helper_functions.is_valid_time(f"{hours}:{minutes}"):
        await interaction.response.send_message(f"Wrong time: {hours}:{minutes}")
        return

    answer = add_record(f"{objective_level} {objective}", zone, f"{hours}:{minutes}")

    if answer:
        await interaction.response.send_message(f'Objective added: {objective_level} {objective} in {zone} at {hours}:{minutes}')
    else:
        await interaction.response.send_message(f'Objective already added.')

@add.autocomplete('objective')
async def objective_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=objective, value=objective)
        for objective in all_objectives if current.lower() in objective.lower()
    ]

@add.autocomplete('zone')
async def zone_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=zone, value=zone)
        for zone in all_zones if current.lower() in zone.lower()
    ]

@add.autocomplete('objective_level')
async def objective_level_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=objective_level, value=objective_level)
        for objective_level in all_objective_levels if current.lower() in objective_level.lower()
    ]

@bot.command()
async def add_manual(ctx, type_: str, map_: str, time_until: str):
    if add_record():
        add_record(type_, map_, time_until)
    else:
        await ctx.send("Record with similar data already exists!")

def add_record(type_: str, map_: str, time_until: str):
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
                #await ctx.send("Record with similar data already exists!")
                return False

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
        return True
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
    embed = discord.Embed(title=f"Current objectives:", color=0x03f8fc)

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
    
    body_records = []
    for row in data:
        if row[0] == 'Type':
            continue

        body_records.append(transform_single_objective(row[:4]))
        type(body_records)
    
    # good example of table2ascii implementation, but no emojis
    # if body_records:
    #     output = t2a(
    #     #header=["Rank", "Team", "Kills", "Position Pts"],
    #     body=body_records,
    #     style=PresetStyle.thin_compact,
    #     alignments=Alignment.LEFT,
    #     )
    if body_records:
        output = draw_table(body_records)
    else:
        output = ":weary: :weary: **No objectives! Find something!** :weary: :weary:"

    # output = t2a(
    #     header=["Rank", "Team", "Kills", "Position Pts", "Total"],
    #         body=[
    #             [1, 'Team A', 2, 4, 6], 
    #             [2, 'Team B', 3, 3, 6], 
    #             [3, 'Team C', 4, 2, 6]],
    #         style=PresetStyle.thin_compact
    #     )

    ## Embed implementation
    #for record in data:
    #    embed.add_field(name="Objectives", value=f'{record[0]}', inline=True)
        
    #await output_channel.send(embed=embed)  

    # Update the bot's message if it exists, else send a new one
    if bot_message:
        await bot_message.edit(content=f"\n{output}\n")
    else:
        await output_channel.send(content=f"\n{output}\n")

bot.run(os.environ["DISCORD_TOKEN"])

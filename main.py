# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands, tasks
import services.spreadsheet
from datetime import datetime, timedelta
from discord import app_commands
import logging
from typing import List

logging.basicConfig(level=logging.ERROR)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_ids=[700787012525097050])
#client = discord.Client(intents=intents)
#tree = app_commands.CommandTree(client)
#tree = app_commands.CommandTree(bot)
sheet = services.spreadsheet.SpreadSheet("objectives_list", "Upcoming Objectives")
records_in_memory = sheet.get_all_records()
time_utc_column_num = 3

zones = [
    'Sunstrand Shoal', 'Frostspring Vulcano', 'Frostspring Passage', 'Southgrove Thicket', 'Sunstrand Quicksands', 'Stonemouth Southbluff', 'Stonemouth Bay', 'Dryvein Steppe', 'Southgrove Copse', 'Sunstrand Dunes', 'Sunstrand Delta', 'Stonemouth Northbluff', 'Avalanche Incline', 'Avalanche Ravine', 'Battlebrae Flatland', 'Battlebrae Grassland', 'Battlebrae Lake', 'Battlebrae Meadow', 'Battlebrae Peaks', 'Battlebrae Plain', 'Bleachskull Desert', 'Bleachskull Steppe', 'Braemore Lowland', 'Braemore Upland', 'Brambleshore Hinterlands', 'Darkbough Snag', 'Deadpine Forest', 'Deathwisp Bog', 'Deathwisp Sink', 'Deepwood Copse', 'Deepwood Dell', 'Deepwood Gorge', 'Deepwood Pines', 'Driftwood Glen', 'Driftwood Hollow', 'Driftwood Vale', 'Drownfield Course', 'Drownfield Fen', 'Drownfield Mire', 'Drownfield Quag', 'Drownfield Rut', 'Drownfield Sink', 'Drownfield Slough', 'Drownfield Wetland', 'Drybasin Oasis', 'Drybasin Riverbed', 'Drytop Pillars', 'Drytop Riverbed', 'Dryvein Confluence', 'Dryvein Cross', 'Dryvein End', 'Dryvein Oasis', 'Dryvein Plain', 'Dryvein Riverbed', 'Everwinter Crossing', 'Everwinter Expanse', 'Everwinter Gap', 'Everwinter Gorge', 'Everwinter Incline', 'Everwinter Passage', 'Everwinter Peak', 'Everwinter Plain', 'Everwinter Reach', 'Everwinter Shores', 'Farshore Bay', 'Farshore Cape', 'Farshore Drylands', 'Farshore Esker', 'Farshore Heath', 'Farshore Lagoon', 'Firesink Caldera', 'Firesink Trench', 'Flammog Desolation', 'Flammog Fork', 'Flammog Valley', 'Flatrock Cliffs', 'Flatrock Plateau', 'Floatshoal Bight', 'Floatshoal Fissure', 'Floatshoal Floe', 'Frostbite Chasm', 'Frostbite Mountain', 'Frostpeak Ascent', 'Frostpeak Vista', 'Frostseep Crevasse', 'Frostseep Ravine', 'Giantweald Copse', 'Giantweald Dale', 'Giantweald Edge', 'Giantweald Glade', 'Giantweald Roots', 'Giantweald Woods', 'Glacierbreak Summit', 'Glacierfall Canyon', 'Glacierfall Cross', 'Glacierfall Fissure', 'Glacierfall Pass', 'Glacierfall Passage', 'Glacierfall Valley', 'Gravemound Brim', 'Gravemound Cliffs', 'Gravemound Hills', 'Gravemound Knoll', 'Gravemound Slope', 'Greenhollow Copse', 'Greenhollow Vale', 'Greenshore Bay', 'Greenshore Peninsula', 'Highstone Grassland', 'Highstone Loch', 'Highstone Meadow', 'Highstone Mound', 'Highstone Plains', 'Highstone Plateau', 'Hightree Borderlands', 'Hightree Cliffs', 'Hightree Dale', 'Hightree Enclave', 'Hightree Glade', 'Hightree Hillock', 'Hightree Isle', 'Hightree Lake', 'Hightree Levee', 'Hightree Pass', 'Hightree Portal East', 'Hightree Portal North', 'Hightree Portal West', 'Hightree Steep', 'Hightree Strand', 'Iceburn Cliffs', 'Iceburn Firth', 'Iceburn Peaks', 'Iceburn Tundra', 'Longfen Arms', 'Longfen Marsh', 'Longfen Veins', 'Meltwater Bog', 'Meltwater Channel', 'Meltwater Delta', 'Meltwater Sump', 'Mudfoot Mounds', 'Mudfoot Sump', 'Munten Fell', 'Munten Rise', 'Munten Tundra', 'Murdergulch Cross', 'Murdergulch Divide', 'Murdergulch Gap', 'Murdergulch Ravine', 'Murdergulch Trail', 'Northstrand Beach', 'Northstrand Dunes', 'Parchsand Cliffs', 'Parchsand Drought', 'Razorrock Bank', 'Razorrock Chasm', 'Razorrock Edge', 'Razorrock Gulch', 'Razorrock Passage', 'Razorrock Ravine', 'Razorrock Valley', 'Razorrock Verge', 'Redtree Enclave', 'Rivercopse Crossing', 'Rivercopse Curve', 'Rivercopse Fount', 'Rivercopse Path', 'Runnelvein Bog', 'Runnelvein Sink', 'Runnelvein Slough', 'Sandmount Ascent', 'Sandmount Desert', 'Sandmount Esker', 'Sandmount Strand', 'Sandrift Coast', 'Sandrift Dunes', 'Sandrift Expanse', 'Sandrift Fringe', 'Sandrift Portal East', 'Sandrift Portal North', 'Sandrift Portal West', 'Sandrift Prairie', 'Sandrift Shore', 'Sandrift Steppe', 'Scuttlesink Marsh', 'Scuttlesink Mouth', 'Scuttlesink Pools', 'Shaleheath Hills', 'Shaleheath Steep', 'Skullmarsh Lower', 'Skullmarsh Upper', 'Skylake Bridge', 'Skylake Hinterlands', 'Skysand Plateau', 'Skysand Ridge', 'Slakesands Canyon', 'Slakesands Mesa', 'Southgrove Escarp', 'Springsump Basin', 'Springsump Melt', 'Springsump Wetland', 'Stonelake Fields', 'Stonelake Hillock', 'Sunfang Approach', 'Sunfang Cliffs', 'Sunfang Dawn', 'Sunfang Ravine', 'Sunfang Wasteland', 'Sunkenbough Spring', 'Sunkenbough Woods', 'Swiftsands Basin', 'Swiftsands Chaparral', 'Swiftsands Plain', 'Thirstwater Gully', 'Thirstwater Steppe', 'Thirstwater Waste', 'Thunderrock Ascent', 'Thunderrock Draw', 'Thunderrock Rapids', 'Thunderrock Upland', 'Timberscar Copse', 'Timberscar Dell', 'Timberslope Bridge', 'Timberslope Dell', 'Timberslope Grove', 'Timbertop Dale', 'Timbertop Escarp', 'Timbertop Wood', 'Twinchannel Narrows', 'Watchwood Bluffs', 'Watchwood Grove', 'Watchwood Lakeside', 'Watchwood Precipice', 'Westweald Shore', 'Westweald Thicket', 'Wetgrave Bog', 'Wetgrave Marsh', 'Wetgrave Swale', 'Whitebank Cross', 'Whitebank Descent', 'Whitebank Portal East', 'Whitebank Portal North', 'Whitebank Portal South', 'Whitebank Ridge', 'Whitebank Shore', 'Whitebank Stream', 'Whitebank Wall', 'Whitecliff Expanse', 'Whitecliff Peak', 'Whitepeak Ascent', 'Whitepeak Spring', 'Whitepeak Tundra', 'Whitewall Pass', 'Whitewall Ridge', 'Widemoor Delta', 'Widemoor End', 'Widemoor Estuary', 'Widemoor Fen', 'Widemoor Flats', 'Widemoor Hills', 'Widemoor Pool', 'Widemoor Portal North', 'Widemoor Portal South', 'Widemoor Portal West', 'Widemoor Shore', 'Widemoor Woods', 'Willowshade Hills', 'Willowshade Icemarsh', 'Willowshade Lake', 'Willowshade Mire', 'Willowshade Pools', 'Willowshade Sink', 'Willowshade Wetlands', 'Windgrass Border', 'Windgrass Coast', 'Windgrass Fields', 'Windgrass Gully', 'Windgrass Portal North', 'Windgrass Portal South', 'Windgrass Portal West', 'Windgrass Precipice', 'Windgrass Rill', 'Windgrass Terrace'
]


OUTPUT_CHANNEL_NAME = "main"
dt_format = '%Y-%m-%d %H:%M:%S'

@bot.event
async def on_ready():
    await bot.tree.sync()
    update_output_channel.start()
    if not update_sheet.is_running():
        update_sheet.start()
    print(f"Slaya ama ready")

#@bot.tree.command()
#async def slash(interaction: discord.Interaction, number: int, string: str):
#    await interaction.response.send_message(f'{number=} {string=}', ephemeral=True)

# Can also specify a guild here, but this example chooses not to.
#tree.add_command(slash)

@bot.tree.command(name="addnew",description="Add objective new")
async def slash_command_tree(interaction:discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}', ephemeral=True)

@bot.tree.command()
async def fruits(interaction: discord.Interaction, fruits: str):
    await interaction.response.send_message(f'Your favourite fruit seems to be {fruits}')

@fruits.autocomplete('add')
async def fruits_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
    return [
        app_commands.Choice(name=fruit, value=fruit)
        for fruit in fruits if current.lower() in fruit.lower()
    ]

## Working approach
#@bot.tree.command(name="add",description="Add objective")
#async def slash_command(interaction:discord.Interaction):
#    await interaction.response.send_message("Hello World!")


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

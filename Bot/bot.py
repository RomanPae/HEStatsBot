# bot.py
import os
import random
import json

import pandas as pd

import psycopg2 as pg

import discord
from discord.ext import commands
from dotenv import load_dotenv

from pyracing.client import Client
import asyncio

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
# Discord Bot Token
TOKEN = os.getenv("DISCORD_TOKEN")

# database information
PG_USERNAME = os.getenv("PG_USERNAME")
PG_DB_NAME = os.getenv("PG_DB_NAME")
PG_PW = os.getenv("PG_PW")
PG_DB_HOST = os.getenv("PG_DB_HOST")

bot = commands.Bot(command_prefix="!")

try:
    conn = pg.connect(
        host=PG_DB_HOST,
        database=PG_DB_NAME,
        user=PG_USERNAME,
        password=PG_PW)
    print("Connection to Database established!")
except:
    print("Connection to database failed!")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# @bot.command(name="update", help="does nothing")
# @commands.has_role("bot-verwalter")
# async def update_data(ctx):
#     #fully clear the list, so that there are no issues with doubling because of appending
#     global driver_list
#     driver_list.clear()
#     for driver in _config ["driver_ids"]:
#         print(f"searching for {driver}")
#         try:
#             driver_data = await ir.driver_stats(search=driver)
#             driver_list.append(driver_data)
#         except: 
#             print (f"Problem with {driver}")
#             pass
    
#     # Put everything into a DataFrame so its easy to sort etc.
#     incidents_avg, display_name, irating, license_class = [], [], [], []
#     for driver in driver_list:
#         display_name.append(driver[0].display_name)
#         irating.append(driver[0].irating)
#         incidents_avg.append(driver[0].incidents_avg)
#         license_class.append(driver[0].license_class)
#     #small helper dict    
#     dict = {"display_name": display_name , "irating": irating , "incidents_avg": incidents_avg, "license_class": license_class}   
#     driver_df = pd.DataFrame(dict)
#     # remove the old pickle if it exists
#     try:
#         os.remove("driver_df.pkl")
#     except:
#         pass
#     #pickle the dataframe for later use
#     driver_df.to_pickle("driver_df.pkl")

#     await ctx.send('Finished')

@bot.command(name="ranking", help="shows ranking of team drivers")
@commands.has_role("driver")
async def ranking(ctx):
    cur = conn.cursor()

    cur.execute("""
    SELECT name, irating FROM team_drivers
    WHERE irating > 0
    ORDER BY irating DESC;
    """)
    irating_list = cur.fetchall()
    cur.close()

    embed = discord.Embed(title=f"", color=0x03f8fc,timestamp= ctx.message.created_at)

    # create Title
    value = "--"
    name = "Team ranking iRating"
    embed.add_field(name=name, value=value, inline=False)

    i = 1
    pos, display_name, irating = [], [], []
    for name, rating in irating_list:
        pos.append(f'{i}')
        display_name.append(f' {name} ')
        irating.append(f' {rating} ')
        i = i+1
        #license_class.append(f' {irating_dict["license_class"][i]} '[:6])

    # create Field for Team Position
    value = "\n".join(pos)
    name = "P"
    embed.add_field(name=name, value=value, inline=True)

    # create Field for Driver
    value = "\n".join(display_name)
    name = "Driver"
    embed.add_field(name=name, value=value, inline=True)

    # create Field for Rating
    value = "\n".join(irating)
    name = "iR"
    embed.add_field(name=name, value=value, inline=True)
    
    await ctx.send(embed = embed)

    # # clean up for the next message
    # embed.clear_fields()
    # # create Title
    # value = "--"
    # name = "Team ranking Incidents"
    # embed.add_field(name=name, value=value, inline=False)
    # incs_dict = driver_df.sort_values(by="incidents_avg", ascending=True, ignore_index=True).to_dict()
    # pos, display_name, incs, license_class = [], [], [], []
    # for i in range(len(incs_dict["display_name"])):
    #     pos.append(f'{i+1}')
    #     display_name.append(f' {incs_dict["display_name"][i]} ')
    #     incs.append(f' {incs_dict["incidents_avg"][i]} ')
    #     #license_class.append(f' {incs_dict["license_class"][i]} ')

    # # create Field for Position
    # value = "\n".join(pos)
    # name = "P"
    # embed.add_field(name=name, value=value, inline=True)

    # # create Field for Driver
    # value = "\n".join(display_name)
    # name = "Driver"
    # embed.add_field(name=name, value=value, inline=True)

    # # create Field for Rating
    # value = "\n".join(incs)
    # name = "avg. incs"
    # embed.add_field(name=name, value=value, inline=True)

    # # create Field for License
    # #value = "\n".join(license_class)
    # #name = "License"
    # #embed.add_field(name=name, value=value, inline=True)
    
    # await ctx.send(embed = embed)



# @bot.command(name="current", help="show current world records for TCC and IMPC")
# @commands.has_role("driver")
# async def current_series(ctx):
    
#     print("current series command called")
#     seasons_list = await ir.current_seasons()
#     current_week = seasons_list[0].race_week
#     embed = discord.Embed(title=f"", color=0x03f8fc,timestamp= ctx.message.created_at)
#     for season in seasons_list:
#         if (season.series_name_short == "IMSA Michelin Pilot Challenge" or season.series_name_short == "Touring Car Challenge"):
#             track = season.tracks[current_week-1]

#             name =f'__**{season.series_name_short} ({season.season_year} S{season.season_quarter} week {current_week})**__'
#             value = f'{track.name} ({track.config})'
#             embed.add_field(name=name, value = value, inline=False)
#             for car in season.cars:
#                 name = f'**{car.name}**'
#                 value = "--"
#                 embed.add_field(name=name, value = value, inline=False)

#                 print(f"fetching data for {car.name}")
#                 WR = await ir.world_records(year=season.season_year, quarter=season.season_quarter, track_id=track.id, car_id= car.id)  
#                 print("finished")            
#                 driver, times = [], []
#                 for i in range(3):
#                     driver.append(f"{i+1} {WR[i].display_name}")
#                     times.append(WR[i].race +" "+  WR[i].qualify +" "+ WR[i].practice)

#                 # create Field for Driver
#                 value = "\n".join(driver)
#                 name = "Driver"
#                 embed.add_field(name=name, value=value, inline=True)

#                 # create Field for Race time
#                 value = "\n".join(times)
#                 name = "Race Qualy Practice"
#                 embed.add_field(name=name, value=value, inline=True)
            
#             print(f"trying to send output with length: {len(embed)}")
#             await ctx.send(embed = embed)
#             embed.clear_fields()

#@bot.command(name="TCC", help="Get TCC season information")
#@commands.has_role("driver")
# async def TCC(ctx):
#     # get season ID
#     seasons_list = await ir.current_seasons()
#     for season in seasons_list:
#         if (season.series_name_short == "Turn Racing Touring Car Challenge"):
#             TCC_season = season 

# @bot.command(name="string", help="Test command for string output")
# @commands.has_role("driver")
# async def string_test(ctx):
#     embed = discord.Embed(title=f"", color=0x03f8fc,timestamp= ctx.message.created_at)
#     name = "Vorname"
#     value = "Hans\n Dieter"
#     embed.add_field(name=name, value=value, inline=True)
#     name = "Nachname"
#     value = "Wurst\n Mücke"
#     embed.add_field(name=name, value=value, inline=True)
#     await ctx.send(embed = embed)
    

#@bot.command(name='roll_dice', help='Simulates rolling dice.')
#@commands.has_role("driver")
# async def roll(ctx, number_of_dice: int, number_of_sides:int):
#     dice = [
#         str(random.choice(range(1, number_of_sides + 1)))
#         for _ in range(number_of_dice)
#     ]
#     await ctx.send(', '.join(dice))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Do I know you?')

bot.run(TOKEN)
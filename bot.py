import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents) # If you wish you can change the prefix.

user_clockins = {}
user_totals = {}

DATA_FILE = "datalogs.json" # make sure to name the file as it says 

def load_totals():
    global user_totals
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            user_totals = {int(k): timedelta(seconds=v) for k, v in data.items()}

def save_totals():
    with open(DATA_FILE, "w") as f:
        json.dump({str(k): v.total_seconds() for k, v in user_totals.items()}, f)

load_totals()  

ADMIN_IDS = { Place admin ids here }  # Admins can add or remove time from the database

RESTRICTED_ROLE_NAME = "Place role here"  # Name of the role to restrict from using commands for example the civ role in your discord

def format_duration(td: timedelta) -> str:
    hrs = int(td.total_seconds() // 3600)
    mins = int((td.total_seconds() % 3600) // 60)
    return f"{hrs} hour(s) and {mins} minute(s)"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Event handler to block commands for users with the restricted role
@bot.event
async def on_message(message):
    # If the message author has the restricted role, ignore the message
    if any(role.name == RESTRICTED_ROLE_NAME for role in message.author.roles):
        return  # Don't process commands for these users
    
    # If the message is not from a bot, process commands
    if not message.author.bot:
        await bot.process_commands(message)

@bot.command(name="clockin")
async def clock_in(ctx):
    await ctx.message.delete()
    uid = ctx.author.id
    if uid in user_clockins:
        embed = discord.Embed(
            title="⛔ Already Clocked In",
            description=f"{ctx.author.mention}, you’re already clocked in!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return
    user_clockins[uid] = datetime.now()
    embed = discord.Embed(
        title="✅ Clocked In",
        description=f"{ctx.author.mention} clocked in at **{user_clockins[uid].strftime('%H:%M:%S')}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    return

@bot.command(name="clockout")
async def clock_out(ctx):
    await ctx.message.delete()
    uid = ctx.author.id
    if uid not in user_clockins:
        embed = discord.Embed(
            title="⛔ Not Clocked In",
            description=f"{ctx.author.mention}, you can’t clock out before clocking in!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    start = user_clockins.pop(uid)
    elapsed = datetime.now() - start
    user_totals[uid] = user_totals.get(uid, timedelta()) + elapsed
    save_totals()  # 🔴 Save to file here
    embed = discord.Embed(
        title="🔚 Clocked Out",
        description=(
            f"{ctx.author.mention} clocked out at **{datetime.now().strftime('%H:%M:%S')}**\n"
            f"Worked: **{format_duration(elapsed)}**"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    return

# Your other command handlers remain the same...

bot.run("YOUR BOT TOKEN HERE")
# to run the bot in your terminal paste this - python bot.py
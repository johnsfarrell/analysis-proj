print("importing")
import discord
from os import getenv
from dotenv import load_dotenv
from tickerapi import Tickers
import botcommands
from pymongo import MongoClient

print("connecting to dotenv")
load_dotenv()

# Discord Bot Startup
print("connecting to discord")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
bot = discord.Client(intents=discord.Intents.all())

# Database Startup
print("connecting to database")
CLUSTER = getenv("DATABASE_CLUSTER")
client = MongoClient(CLUSTER)
db = client.stocks.tickers

## Bot is ready
@bot.event
async def on_ready():
    await update_status()

async def update_status():
    num_graded = len(list(db.find({})))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Graded: " + str(num_graded)), status=discord.Status.do_not_disturb)


## Message is sent in guild
@bot.event
async def on_message(message):
    m = message.content
    a = message.author
    if a == bot.user:
        return
    elif m.startswith("!r"):
        await botcommands.respond_random(message)
    elif m == "!top":
        await botcommands.respond_top(message, db)
    elif m == "!bottom":
        await botcommands.respond_bottom(message, db)
    elif m == "!auto":
        await botcommands.respond_auto(message, db, bot)
    elif m == "!stopauto":
        await botcommands.respond_stopauto(message, bot)
    else:
        for t in m.split(","):
            await botcommands.respond_ha(t, message, db)
    await update_status()

bot.run(DISCORD_TOKEN)
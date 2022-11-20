import random
from tickerapi import Tickers
from analysis import fundamentalAverage
from datetime import datetime
import discord

# mongo document template
def to_json(ticker, ha, na):
    return {
        "ticker": ticker,
        "hegeman_average": ha,
        "number_analysts": na,
        "date": datetime.utcnow()
    }

# returns parsed random list 
#  "['abc','123']" -> "abc,123"
def randomList(lst, n: int):
    return str(random.choices(lst, k=n)).replace("', '", ",")

# gets a ticker response
async def respond_ha(ticker, message, db):
    if ticker.upper() in Tickers:
        # base message
        reply = await message.reply('*Fetching a response for ' + ticker.upper() + '... 0%*')
        try:
            # search db
            response = db.find_one({"ticker": ticker.upper()})
            # if not in db
            if response is None:
                (fa, na) = await fundamentalAverage(ticker, reply)
                # only save data to db if its valid
                if fa > 1 and na > 1:
                    db.insert_one(to_json(ticker.upper(), fa, na))
                    await reply.edit(content="Hegeman's Average for " + ticker.upper() + " is **" + str(fa) + "**. (" + str(na) + " analysts)")
                else:
                    await reply.edit(content="Ticker was either invalid or didn't have enough data.")
            # if in db
            else:
                await reply.edit(content="Hegeman's Average for " + ticker.upper() + " is **" + str(response['hegeman_average']) + "**. (" + str(response['number_analysts']) + " analysts)")
        except:
            await reply.edit(content="Ticker was either invalid or doesn't have enough data.")

# !top - returns top grades
async def respond_top(message, db):
    try: 
        response = db.find({}).limit(20).sort("hegeman_average")
        response_body = "**Top Hegeman's Average Discovered (HA, NA)**\n"
        for i, n in enumerate(response):
            response_body += "`" + str("%02d" % (i + 1,)) + ". " + n["ticker"] + " (" + str(n["hegeman_average"]) + ", " + str(n["number_analysts"]) + ")`\n"
        await message.reply(response_body)
    except:
        await message.reply("Error returning top discovered HA's.")

# !auto - automatic grading
async def respond_auto(message, db, bot):
    global hault_auto
    hault_auto = False
    catchedup = False
    amount = len(Tickers)
    for i, n in enumerate(Tickers):
        if not hault_auto:
            if catchedup:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="AUTO: " + str(i) + "/" + str(amount)), status=discord.Status.do_not_disturb)
                await respond_ha(n, message, db)
            elif n == "TKGBY":
                catchedup = True
        else:
            return
    await message.reply("Finished auto grading! (" + str(amount) + "/" + str(amount) + ")")

# !stopauto - stops auto grading
async def respond_stopauto(message, bot):
    global hault_auto
    hault_auto = True
    await message.reply("Auto grading haulted.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="v1.0"), status=discord.Status.do_not_disturb)


# !bottom - returns
async def respond_bottom(message, db):
        response = list(db.find({}).sort("hegeman_average"))[-21:-1]
        response = reversed(response)
        response_body = "**Top Hegeman's Average Discovered (HA, NA)**\n"
        for i, n in enumerate(response):
            response_body += "`" + str("%02d" % (i + 1,)) + ". " + n["ticker"] + " (" + str(n["hegeman_average"]) + ", " + str(n["number_analysts"]) + ")`\n"
        await message.reply(response_body)

# !r - returns random stocks
async def respond_random(message):
    try: 
        m = message.content + " 1"
        await message.reply("`" + randomList(Tickers, int(m.split(" ")[1]))[2:-2] + "`")
    except:
        await message.reply("!r [integer 1 to 300]")
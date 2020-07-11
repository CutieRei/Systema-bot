import discord,asyncio
from discord.ext import commands
import aiosqlite as sql

async def get_prefix(bot,msg):
    pre = [f"<@!{bot.user.id}> ",f"<@{bot.user.id}> ","s."]
    return pre
bot = commands.Bot(command_prefix=get_prefix,help_command=None,case_insensitive=True)
token = ""
with open("./private/token.txt",'r') as tk:
    token = tk.read()

extend = []
with open("config.txt","r") as txt:
    extend = txt.read().split(",")
for ext in extend:
    bot.load_extension("cogs."+ext)

@bot.command()
@commands.is_owner()
async def reload(ctx):
    async with ctx.channel.typing():
        for i in extend:
            await asyncio.sleep(0.25)
            bot.reload_extension("cogs."+i)
        await ctx.send("Reloaded all cogs")

@bot.command()
@commands.is_owner()
async def load(ctx):
    async with ctx.channel.typing():
        for i in extend:
            await asyncio.sleep(0.25)
            bot.load_extension("cogs."+i)


bot.run(token, reconnect=True)
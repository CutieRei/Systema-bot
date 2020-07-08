import discord,asyncio
from discord.ext import commands

def get_prefix(bot,msg):
    pre = [f"<@!{bot.user.id}> ",f"<@{bot.user.id}> ","s."]
    return pre
bot = commands.Bot(command_prefix=get_prefix,help_command=None)
token = ""
with open("./private/token.txt",'r') as tk:
    token = tk.read()

extend = ["event","admin"]
for ext in extend:
    bot.load_extension("cogs."+ext)

@bot.command()
@commands.has_role("Developers")
async def reload(ctx):
    async with ctx.channel.typing():
        for i in extend:
            await asyncio.sleep(0.25)
            bot.reload_extension("cogs."+i)
        await ctx.send("Reloaded all cogs")


bot.run(token, reconnect=True)
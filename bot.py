import os

from discord.ext import commands


async def get_prefix(b, m):
    pre = [f"<@!{b.user.id}> ", f"<@{b.user.id}> ", "s."]
    return pre


bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)
with open("./private/token.txt", "r") as txt:
    token = txt.read()
for ext in os.listdir("./cogs"):
    if ext.endswith(".py"):
        bot.load_extension("cogs." + ext[:-3])


@bot.command()
@commands.is_owner()
async def reload(ctx):
    async with ctx.channel.typing():
        for i in os.listdir("./cogs"):
            if i.endswith(".py"):
                bot.reload_extension("cogs." + i[:-3])
    await ctx.send("Reloaded all cogs")


@bot.command()
@commands.is_owner()
async def load(ctx):
    async with ctx.channel.typing():
        for i in os.listdir("./cogs"):
            try:
                bot.load_extension("cogs." + i)
            except Exception:
                pass
    await ctx.send("Loaded cogs!")


bot.run(token, reconnect=True)

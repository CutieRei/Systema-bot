import random
import re

import aiohttp
from discord import Embed
from discord.ext import commands


class Nsfw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rule34(self, ctx, tags):
        """
        Get random image from rule34 by tags, for you 👀 weebs maybe.
        """
        session = aiohttp.ClientSession()
        msg = await ctx.send("Please wait while im fetching.....")
        if ctx.channel.is_nsfw() or re.match(r".*nsfw-not.*", ctx.channel.name, re.IGNORECASE):
            yeah = False
            async with ctx.channel.typing():
                card = Embed(
                    title="nsfw.png"
                )
                tags = tags.replace(" ", "_")
                async with session.get(f"https://r34-json-api.herokuapp.com/posts?tags={tags}") as r:
                    data = await r.json()
                    if len(data) == 0:
                        pass
                    else:
                        yeah = True
                        data = random.choice(data)
                        card.set_image(url=data["file_url"])
            if yeah:
                await ctx.send(embed=card, content=None)
                await msg.delete()
            else:
                await ctx.send(content="Either that tag doesn't exists or the connection is having an issue")
                await msg.delete()
            await session.close()
        else:
            await msg.edit(content="Not in nsfw channel!")
            await session.close()


def setup(bot):
    print("#Loaded nsfw")
    bot.add_cog(Nsfw(bot))

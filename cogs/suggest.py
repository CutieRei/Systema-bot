import re
from datetime import datetime

import discord
from discord.ext import commands


class Suggest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def suggest(self, ctx):
        """
        Suggest something if there's no Suggestion channels the Suggestion is aborted
        """
        okokok = False
        for i in ctx.guild.text_channels:
            if re.match(r".*suggestion.*", i.name, re.IGNORECASE):
                okokok = True

        if okokok:
            await ctx.message.delete()
            msg1 = await ctx.send("Whats the Suggestion? type `cancel` to abort suggestion")
            card = discord.Embed(
                color=discord.Color.from_rgb(102, 153, 204),
                timestamp=datetime.utcnow(),
                title=f"{str(ctx.author)}\nNew Suggestion!"
            )

            def check(msg):
                if msg.author == ctx.author:
                    return True

            head = await self.bot.wait_for('message', check=check)
            if head.content.lower() == "cancel":
                await msg1.delete()
                await head.delete()
                await ctx.send("Suggestion aborted")
            else:
                await msg1.delete()
                await head.delete()
                msg2 = await ctx.send("Whats your description of the suggestion?")
                desc = await self.bot.wait_for('message', check=check)
                card.add_field(name="Title", value=head.content)
                card.add_field(name="Description", value=desc.content)
                await msg2.delete()
                await desc.delete()
                channel = None
                pattern = r".*suggestion.*"
                for i in ctx.guild.text_channels:
                    if re.match(pattern, i.name, re.I):
                        channel = i

                suggest = await channel.send(embed=card)
                await suggest.add_reaction("✅")
                await suggest.add_reaction("❎")
                await ctx.send("Suggestion posted!")
        else:
            await ctx.send("Dont have Suggestion channel please use init_suggest")


def setup(bot):
    print("#Loaded suggest")
    bot.add_cog(Suggest(bot))

from discord import Embed
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gay"])
    async def gayness(self, ctx, *, who):
        """
            Check gayness of a person or something 👀 (dedicated to CodeJabo)
            """
        if len(who) > 100:
            await ctx.send("No spam word")
        else:
            who1 = int(str(sum([ord(i) for i in who]))[-2:])
            random.seed(int(who1))
            who1 = random.randint(0, 200)
            if who.lower() in ["jabo", "jabolesbo"]:
                who1 = 0
            if who.lower() in ["saltydumpling", "saltydumplings"]:
                who1 = random.randint(1000, 10000)
            card = Embed(
                title=f"{who1}% Gayness"
            )
            if who1 > 150:
                card.description = "VERY VERY GAY YOU ARE GAYESS OF THE GAY"
            elif who1 > 100:
                card.description = "Wow so gay🏳️‍🌈"
            elif who1 > 80:
                card.description = "Wow, gay?"
            elif who1 > 35:
                card.description = "Idk, gay...👀"
            elif who1 > 1:
                card.description = "Not really gey"
            elif who1 == 0:
                card.description = "Not gay whatsoever"
            await ctx.send(embed=card)
            random.seed(0)

    @commands.command()
    async def say(self, ctx, *, message):
        """
            Repeat a word or a sentence you give as argument
            """
        await ctx.send(message)


def setup(bot):
    print("#Loaded fun")
    bot.add_cog(Fun(bot))

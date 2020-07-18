import discord,aiohttp
from discord.ext import commands,tasks
from discord import Embed,Colour
from datetime import datetime


class Growtopia(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def render(self,ctx,world):
        """
        Render a world from growtopia
        """
        session = aiohttp.ClientSession()
        card = Embed(
        title=f"Render of world **{world.upper()}**"
        )
        yes = None
        async with ctx.channel.typing():
            render=f"https://growtopiagame.com/worlds/{world.lower()}.png"
            async with session.get(render) as r:
                if r.status == 200:
                    card.set_image(url=render)
                    yes = True
                elif r.status in [404,403]:
                    yes = False
                else:
                    yes = None
        if yes:
            await ctx.send(embed=card)
        elif not yes:
            await ctx.send("That world is not rendered yet")
        elif yes is None:
            await ctx.send(r.status_code)
        await session.close()
    
    @commands.command(aliases=["stats"])
    async def status(self,ctx):
        """
        Check growtopia status
        """
        session = aiohttp.ClientSession()
        async with ctx.channel.typing():
            async with session.get("https://growtopiagame.com/detail") as r:
                data = await r.json(content_type="text/html")
                if int(data["online_user"]) < 10:
                    status = "Offline"
                    colour = (255,100,0)
                else:
                    colour = (0,255,100)
                    status = "Online"
                card = Embed(
                colour=Colour.from_rgb(colour[0],colour[1],colour[2]),
                title="Status for Growtopia server",
                description=f"Status: **{status}**\nPlayers: **{data['online_user']}**"
                )
                await ctx.send(embed=card)
        await session.close()

    @commands.command()
    async def wotd(self,ctx):
    	'''
    	Shows growtopia world of the day
    	'''
    	msg = await ctx.send("Fetching.....")
    	async with ctx.channel.typing():
    		session = aiohttp.ClientSession()
    		async with session.get("https://growtopiagame.com/detail") as r:
    			data = await r.json(content_type="text/html")
    			wotd = data["world_day_images"]["full_size"]
    			wotd = wotd.split('/')[-1].split('.png')[0]
    			card = Embed(
    				title=f"Today world of the day is {wotd.upper()}",
    				timestamp=datetime.utcnow()
    			)
    			card.set_image(url=data['world_day_images']["full_size"])
    			await ctx.send(embed=card)
    			await msg.delete()
    			await session.close()

def setup(bot):
    print("#Loaded growtopia")
    bot.add_cog(Growtopia(bot))
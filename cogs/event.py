import discord,random,asyncio
from discord import Embed,Colour
from discord.ext import commands
from datetime import datetime
import aiosqlite as sql
from discord.utils import get

class Event(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ready = False
        self.dc = False
    
    #@commands.Cog.listener()
#    async def on_command_error(self,ctx,err):
#        channel = self.bot.get_channel(730370841581453403)
#        if isinstance(err,commands.CommandError):
#            await channel.send(err)
#        else:
#            await channel.send(err)
            
    
    #async def bot_check(self,ctx):
#        perms = {}
#        for perm,bool in ctx.author.guild_permissions:
#            perms[perm] = bool
#        channel = 729680694527131697
#        if ctx.channel.id != channel and perms["manage_channels"]:
#            return True
#        elif ctx.channel.id != channel and not perms["manage_channels"]:
#            return False
#        else:
#            return True
    
    @commands.Cog.listener()
    async def on_connect(self):
        if self.ready:
            print(f">>{self.bot.user.name} has reconnected")
            self.dc = False
        else:
            print(f">>{self.bot.user.name} has connected")
            async with sql.connect("./db/data.sql") as db:
                print("data> Connected to database")
            self.ready = True
            self.dc = False
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="Muted people :)"))
        print(">>Cache collected!")
        
    @commands.Cog.listener()
    async def on_disconnect(self):
        if self.dc:
            pass
        else:
            print(">>Disconnected")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        chad = get(member.guild.text_channels,id=729680089276481618)
        if chad is None:
            pass
        else:
            sentence = [f"Hello! {member.mention}({str(member)})",f"Grab a bot and have fun in pre-alpha state, {member.mention}({str(member)})"]
            card = Embed(
                title=f"{str(member)} Joined!",
                description=random.choice(sentence),
                timestamp=datetime.utcnow()
            )
            card.set_thumbnail(url=member.avatar_url_as(static_format='png'))
            await chad.send(embed=card)
        user = self.bot.get_user(member.id)
        await user.send(f"Hello {member.name}, Welcome to {member.guild}")

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        pass

def setup(bot):
    print("#Loaded event")
    bot.add_cog(Event(bot))
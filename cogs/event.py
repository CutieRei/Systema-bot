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
                await db.execute('CREATE TABLE IF NOT EXISTS verified(id INTEGER PRIMARY KEY,userid INTEGER,name TEXT,date DATETIME default CURRENT_TIMESTAMP)')
                await db.commit()
                print("data> Connected to database")
            self.ready = True
            self.dc = False
    @commands.Cog.listener()
    async def on_ready(self):
        print(">>Cache collected!")
        
    @commands.Cog.listener()
    async def on_disconnect(self):
        if self.dc:
            pass
        else:
            print(">>Disconnected")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.name == "Systema":
            await asyncio.sleep(1.5)
            async with sql.connect("./db/data.sql") as db:
                await db.execute("INSERT INTO verified (userid,name,date) VALUES (?,?,?)",(member.id,member.name,datetime.utcnow(),))
                await db.commit()

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        if member.guild.name == "System":
            await asyncio.sleep(0.5)
            async with sql.connect("./db/data.sql") as db:
                await db.execute("DELETE FROM verified WHERE userid = ?",(member.id,))
                await db.commit()

def setup(bot):
    print("#Loaded event")
    bot.add_cog(Event(bot))
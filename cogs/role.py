import discord,asyncio
from discord import Embed,Colour
from discord.ext import commands
import aiosqlite as sql
from discord.utils import get


class Role(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        bot.loop.create_task(self.loaded())
    
    async def loaded(self):
        async with sql.connect("./db/data.sql") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS roles_backup(userid INTEGER,name TEXT,roles)")
            await db.execute("CREATE TABLE IF NOT EXISTS muted(id INTEGER,name TEXT,date DATETIME)")
            await db.commit()
    
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        if member.guild.name == "Systema":
            roles = ",".join([i.name for i in member.roles])
            async with sql.connect("./db/data.sql") as db:
                await db.execute("INSERT INTO roles_backup VALUES (?,?,?)",(member.id,member.name,roles))
                await db.commit()
            
    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.guild.name == "Systema":
            async with sql.connect("./db/data.sql") as db:
                async with db.execute("SELECT roles FROM roles_backup WHERE userid = ?",(member.id,)) as c:
                    row = await c.fetchone()
                    if row:
                        guild = member.guild
                        roles = []
                        for i in row[0].split(","):
                            if i != "@everyone":
                                roles.append(get(guild.roles,name=i))
                        for i in roles:
                                await member.add_roles(i)
                        await db.execute("DELETE FROM roles_backup WHERE userid = ?",(member.id,))
                    else:
                        pass

def setup(bot):
    print("#Loaded role")
    bot.add_cog(Role(bot))
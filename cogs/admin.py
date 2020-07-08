import discord,asyncio
from discord import Embed,Colour
from discord.ext import commands
import aiosqlite as sql
from datetime import datetime
from discord.utils import get

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self,ctx,name,*,rgb):
        rgb = rgb.split(",")
        rgb = [int(i) for i in rgb]
        role = await ctx.guild.create_role(name=name,colour=Colour.from_rgb(rgb[0],rgb[1],rgb[2]))
        await ctx.send(f"Created role, Info:\nName: {role.name}\nColour: {role.colour}\nID: {role.id}")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def set(self,ctx):
        await ctx.send("Subcommands:\n1. prefix <prefix>\n2. admin <role>")

    @set.command()
    async def prefix(self,ctx,prefix):
        async with sql.connect('./db/data.sql') as db:
            async with db.execute("SELECT pre FROM prefix WHERE guild = ?",(ctx.guild.id,)) as c:
                row = await c.fetchone()
                if row[0] == prefix:
                    await ctx.send("Familiar text isn't it?")
                if len(prefix) > 5:
                    await ctx.send("Cannot be more than 5 characters")
                else:
                    if row:
                        await db.execute("UPDATE prefix SET pre =? where guild = ?",(prefix,ctx.guild.id,))
                        await db.commit()
                        await ctx.send("Successfully updated prefix")
                    else:
                        await db.execute("INSERT INTO prefix VALUES (?,?)",(ctx.guild.id,prefix))
                        await db.commit()
                        await ctx.send("Successfully added prefix")
    @set.command()
    async def admin(self,ctx,role:discord.Role):
        async with sql.connect("./db/data.sql") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS admins(id INTEGER,name TEXT,guild INTEGER)")
            await db.commit()
            async with db.execute("SELECT id FROM admins WHERE guild = ?",(ctx.guild.id,)) as c:
                row = await c.fetchone()
                if row:
                    await db.execute("UPDATE admins SET id = ?,name = ? WHERE guild = ?",(role.id,role.name,ctx.guild.id,))
                    await db.commit()
                    await ctx.send("Successfully updated Admin role")
                else:
                    await db.execute("INSERT INTO admins VALUES (?,?,?)",(role.id,role.name,ctx.guild.id,))
                    await db.commit()
                    await ctx.send("Successfully added admin role")

                    
    
    @commands.command()
    async def permissions(self,ctx):
        await ctx.send(ctx.guild.me.guild_permissions)
    
    @commands.command(aliases=["clear","yeet"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self,ctx,amount:int=5):
        def check(m):
            if m.pinned:
                return False
            else:
                return True
        async with ctx.channel.typing():
            await asyncio.sleep(0.5)
            deleted = await ctx.channel.purge(limit=amount,check=check)
        card = Embed(
            colour=Colour.from_rgb(0,255,100),
            title=f"Purged {len(deleted)} messages"
        )
        await ctx.send(embed=card, delete_after=3)
            
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self,ctx,member:discord.Member):
        role = role = get(ctx.guild.roles,name="Muted")
        await member.add_roles(role)
        await ctx.send(f"🔇 Muted {member.display_name}")
        async with sql.connect("./db/data.sql") as db:
            await db.execute("INSERT INTO muted (id,name,date) VALUES (?,?,?)",(member.id,member.name,datetime.utcnow(),))
            await db.commit()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self,ctx,member:discord.Member):
        roles = [i.name for i in member.roles]
        role = role = get(ctx.guild.roles,name="Muted")
        if "Muted" in roles:
            await ctx.send(f"🔈 Unmuted {member.display_name}")
            await member.remove_roles(role)
            async with sql.connect("./db/data.sql") as db:
                await db.execute("DELETE FROM muted WHERE id = ?",(member.id,))
                await db.commit()
        else:
            await ctx.send("Member is not muted")
            

    @commands.command()
    async def suggest(self,ctx):
        await ctx.message.delete()
        if ctx.guild.name.lower() == "systema":
            msg1 = await ctx.send("Whats the Suggestion? type `cancel` to abort suggestion")
            card = Embed(
                colour=Colour.from_rgb(102,153,204),
                timestamp=datetime.utcnow(),
                title=f"{str(ctx.author)}\nNew Suggestion!"
            )
            def check(msg):
                if msg.author == ctx.author:
                    return True
            
            head =  await self.bot.wait_for('message',check=check)
            if head.content.lower() == "cancel":
                await msg1.delete()
                await head.delete()
                await ctx.send("Suggestion aborted")
            else:
                await msg1.delete()
                await head.delete()
                msg2 = await ctx.send("Whats your description of the suggestion?")
                desc = await self.bot.wait_for('message',check=check)
                card.add_field(name="Title",value=head.content)
                card.add_field(name="Description",value=desc.content)
                await msg2.delete()
                await desc.delete()
                channel = self.bot.get_channel(729681182928928828)
                suggest = await channel.send(embed=card)
                await suggest.add_reaction("✅")
                await suggest.add_reaction("❎")
                await ctx.send("Suggestion posted!")
        else:
            await ctx.send('Not in main server!')
    
    @commands.command()
    async def say(self,ctx,*,message):
            await ctx.send(message)
    
    @commands.command(aliases=["gay"])
    async def gayness(self,ctx,*,who):
            who1 = sum([ord(i) for i in who])//10
            if who.lower() in ["jabo","jabolesbo"]:
                who1 = 0
            card = Embed(
            title=f"{who1}% Gayness"
            )
            if who1 > 100:
                card.description="Wow so gay🏳️‍🌈"
            elif who1 > 80:
                card.description="Wow, gay?"
            elif who1 > 35:
                card.description="Idk gay...👀"
            elif who1 > 1:
                card.description="Not really gey"
            elif who1 == 0:
                card.description="Not gay whatsoever"
            await ctx.send(embed=card)
            
    @commands.command()
    @commands.has_role("Developers")
    async def dc(self,ctx):
        await ctx.send("Disconnected!")
        await self.bot.logout()

    @commands.Cog.listener()
    async def wait_until_ready():
        async with sql.connect("./db/data.sql") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS muted(id INTEGER PRIMARY KEY,userid INTEGER,name TEXT,date DATETIME")
            await db.commit()


def setup(bot):
    print("#Loaded admin")
    bot.add_cog(Admin(bot))
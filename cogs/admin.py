import discord,asyncio
from discord import Embed,Colour
from discord.ext import commands
import aiosqlite as sql
from datetime import datetime

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
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
    @commands.has_permissions(manage_roles=True)
    async def verify(self,ctx,member:discord.Member):
        async with sql.connect("./db/data.sql") as db:
            async with ctx.channel.typing():
                await asyncio.sleep(1)
                async with db.execute("SELECT * FROM verified WHERE userid = ?",(member.id,)) as row:
                    user = await row.fetchone()
                    if user:
                        await ctx.send("Member already in database")
                    else:
                       await db.execute("INSERT INTO verified (userid,name,date) VALUES (?,?,?)",(member.id,member.name,datetime.utcnow(),))
                       await db.commit()
                       await ctx.send("Successfully added member to database")

    @verify.error
    async def on_command_error(self,ctx,err):
        if isinstance(err,commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: **{err.param.name}**")
        else:
            raise err
            
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self,ctx,member:discord.Member):
        role = ctx.guild.get_role(729936090315620382)
        await member.add_roles(role)
        await ctx.send(f"🔇 Muted {member.display_name}")
        async with sql.connect("./db/data.sql") as db:
            await db.execute("INSERT INTO muted (userid,name,date) VALUES (?,?,?)",(member.id,member.name,datetime.utcnow(),))
            await db.execute()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self,ctx,member:discord.Member):
        roles = [i.name for i in member.roles]
        role = ctx.guild.get_role(729936090315620382)
        if "Muted" in roles:
            await ctx.send(f"🔈 Unmuted {member.display_name}")
            await member.remove_roles(role)
            async with sql.connect("./db/data.sql") as db:
                await db.execute("DELETE FROM muted WHERE userid = ?",(member.id,))
        else:
            await ctx.send("Member is not muted")
            

    @commands.command()
    async def suggest(self,ctx):
        msg1 = await ctx.send("Whats the Suggestion?")
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
        await ctx.send(embed=card)
    
    @commands.command()
    async def say(self,ctx,*,message):
            await ctx.send(message)
    
    @commands.command()
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
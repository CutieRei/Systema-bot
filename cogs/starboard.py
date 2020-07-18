import discord
from discord import Embed,Colour
from discord.ext import commands,tasks
import aiosqlite as sql
from datetime import datetime
from discord.utils import get

class Starboard(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def star(self,ctx,star:int):
        """
        Set star for current server starboard requirements
        """
        async with sql.connect("./db/data.sql") as db:
            async with db.execute("SELECT star FROM board WHERE guild = ?",(ctx.guild.id,)) as c:
                count = await c.fetchone()
                if count:
                    await db.execute("UPDATE board SET star = ? WHERE guild = ?",(star,ctx.guild.id,))
                    await db.commit()
                    await ctx.send("Updated Starboard requirement")
                else:
                    await db.execute("INSERT INTO board VALUES (?,?)",(ctx.guild.id,star,))
                    await db.commit()
                    await ctx.send("Successfully added Starboard requirement")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,pay):
        guild_count = 0
        async with sql.connect("./db/data.sql") as db:
            async with db.execute("SELECT star FROM board WHERE guild = ?",(pay.guild_id,)) as c:
                count1 = await c.fetchone()
                if count1:
                    guild_count = count1[0]
                else:
                    guild_count = 3
        guild = self.bot.get_guild(pay.guild_id)
        channel = get(guild.text_channels,id=pay.channel_id)
        msg = await channel.fetch_message(pay.message_id)
        star = False
        count = 0
        for i in msg.reactions:
            if i.emoji == "⭐" and i.count >= guild_count:
                star = True
                count = i.count
        member = guild.get_member(msg.author.id)
        board = None
        for i in guild.text_channels:
            if re.match(r".*starboard.*",i.name,re.IGNORECASE):
                board = i
        if board:
            if star:
                card = Embed(
                description=msg.content,
                timestamp=datetime.utcnow()
                )
                card.set_author(icon_url=member.avatar_url_as(static_format='png'),name=str(member))
                card.add_field(name="Original",value=f"[Jump!]({msg.jump_url})")
                await board.send(f"🌟{count}",embed=card)

    #@commands.command()
#    @commands.has_permissions(manage_channels=True)
#    async def starboard(self,ctx):
#        already=False
#        pattern = r".*starboard.*"
#        for i in ctx.guild.text_channels:
#            if re.match(pattern,i.name,re.IGNORECASE):
#                already = True
#        if already:
#            await ctx.send('Already have starboard!')
#        if not already:
#            role = get(ctx.guild.roles,name="Systema")
#            everyone = ctx.guild.default_role
#            star = await ctx.guild.create_text_channel("starboard")
#            await star.set_permissions(everyone,send_messages=False)
#            await star.set_permissions(role,send_messages=True)
#            await ctx.send("Successfully created starboard!")

def setup(bot):
    print("#Loaded starboard")
    bot.add_cog(Starboard(bot))
import discord
from discord.ext import commands,tasks
from discord import Embed,Colour
import random,asyncio
import aiosqlite as sql
from datetime import datetime
from discord.ext.commands.cooldowns import BucketType



db_path="./db/game.sql"

async def select_user(id):
        async with sql.connect(db_path) as db:
            async with db.execute("SELECT * FROM data WHERE id = ?",(id,)) as c:
                user = await c.fetchone()
                if user:
                    return {
                        "id":str(user[0]),
                        "level":str(user[1]),
                        "exp":str(user[2]),
                        "money":str(user[3])
                    }
                else:
                    return None

async def insert_user(id):
    values = (id,1,0,0.0,)
    async with sql.connect(db_path) as db:
        await db.execute("INSERT INTO data VALUES (?,?,?,?)",values)
        await db.commit()
    return values
    
async def update_user(id,money,level, exp):
    async with sql.connect(db_path) as db:
        await db.execute("UPDATE data SET exp = ?,level = ?,money = ? WHERE id = ?",(exp,level,money,id,))
        await db.commit()
    return id
    
async def user_work(id):
    user1 = await select_user(id)
    user = user1.copy()
    exp = int(user["exp"])+random.randint(1,100)
    update=[exp,exp//2500,float(user["money"])+random.uniform(1,100)]
    user["exp"] = update[0]
    user["level"] = update[1]
    user["money"] = update[2]
    await update_user(id,user["money"],user["level"],user["exp"])
    return [update,user1]
    

class Game(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    @commands.cooldown(3,20,BucketType.user)
    async def work(self,ctx):
        """
        Work for you character, get XP and Cash.
        """
        data = await user_work(ctx.author.id)
        money = str(data[0][-1]-float(data[-1]["money"]))[:-13]
        if int(data[1]["level"]) < data[0][1]:
            await ctx.send(f"{ctx.author.display_name} Just leveled up to level **{data[0][1]}**")
        await ctx.send(f"You got **{money}$** and **{int(data[0][0])-int(data[1]['exp'])}** exp")
    
    @work.error
    async def work_error(self,ctx,err):
        if isinstance(err,commands.CommandOnCooldown):
            minute = err.retry_after//60
            second = err.retry_after-(minute*60)
            await ctx.send(f"Please retry after **{int(minute)}m** **{int(second)}s**\n**{err.cooldown.rate}** uses per **{err.cooldown.type.name.capitalize()}** for every **{int(err.cooldown.per)}s**")
        else:
            raise err
    @commands.command()
    async def verify(self,ctx):
        """
        Verify yourself so you can have your own character
        """
        async with sql.connect(db_path) as db:
            verified = await select_user(ctx.author.id)
            if verified is None:
                await insert_user(ctx.author.id)
                await ctx.send(f"Verified {ctx.author.mention}")
            else:
                await ctx.send("You already registered")

    @commands.command(aliases=["pf"])
    async def profile(self,ctx,member:discord.Member=None):
        """
        Check profile of someone else or your own
        """
        if member != None and await select_user(member.id):
            data = await select_user(member.id)
            card = Embed(
            title=f"Profile for {member.display_name}",
            description=f"ID: **{data['id']}**\nExp: **{data['exp']}**\nLevel: **{data['level']}**\nMoney: **{int(float(data['money']))}$**",
            colour=Colour.from_rgb(0,100,255),
            timestamp=datetime.utcnow()
            )
            card.set_footer(icon_url=member.avatar_url_as(static_format='png'),text=f"Copyright© {datetime.utcnow().year} ReyterGTX")
            await ctx.send(embed=card)
        elif member is None and await select_user(ctx.author.id):
            data = await select_user(ctx.author.id)
            card = Embed(
            title=f"{ctx.author.display_name} Profile",
            description=f"ID: **{data['id']}**\nExp: **{data['exp']}**\nLevel: **{data['level']}**\nMoney: **{int(float(data['money']))}$**",
            colour=Colour.from_rgb(0,100,255),
            timestamp=datetime.utcnow()
            )
            card.set_footer(icon_url=ctx.author.avatar_url_as(static_format='png'),text=f"Copyright© {datetime.utcnow().year} ReyterGTX")
            await ctx.send(embed=card)
        else:
            await ctx.send("Something went wrong :O")

def setup(bot):
    print("#Loaded games")
    bot.add_cog(Game(bot))
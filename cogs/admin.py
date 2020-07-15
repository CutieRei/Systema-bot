import discord,asyncio
from discord import Embed,Colour
from discord.ext import commands
import aiosqlite as sql
from datetime import datetime
from discord.utils import get
import requests,random,re,aiohttp

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def wotd(self,ctx):
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

    @commands.command()
    async def check(self,ctx,member:discord.Member):
    	roles = []
    	for i in member.roles:
    		if i.name != "@everyone":
    			roles.append(i.name)
    	user = self.bot.get_user(member.id)
    	created = str(user.created_at).split(".")[0]
    	joined = str(member.joined_at).split(".")[0]
    	card = Embed(
    		title=f"Info about {str(member)}",
    		timestamp=datetime.utcnow()
    	)
    	card.set_thumbnail(url=member.avatar_url_as(static_format='png'))
    	card.add_field(name="Joined at",value=f"Member joined this server at **{joined}**")
    	card.add_field(name="Joined discord at",value=f"User joined discord at **{created}**")
    	card.add_field(name="Member roles",value=f"`{','.join(roles)}`")
    	await ctx.send(embed=card)
    
    @commands.command(aliases=["creds"])
    async def credits(self,ctx):
        creator = self.bot.get_user(716503311402008577)
        
        card = Embed(
            colour=Colour.from_rgb(0,100,255),
            title="Credits for Systema bot",
            timestamp=datetime.utcnow()
        )
        card.add_field(name="Creator",value=f"{str(creator)} created this bot")
        card.set_footer(text="This bot is open source and you can use it anyway you want but not make any money from it",icon_url=creator.avatar_url_as(static_format='png'))
        await ctx.send(embed=card)
    
    @commands.command(aliases=["stats"])
    async def status(self,ctx):
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
    @commands.has_permissions(manage_channels=True)
    async def set_star(self,ctx,star:int):
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
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def init_starboard(self,ctx):
        already=False
        pattern = r".*starboard.*"
        for i in ctx.guild.text_channels:
            if re.match(pattern,i.name,re.IGNORECASE):
                already = True
        if already:
            await ctx.send('Already have starboard!')
        if not already:
            role = get(ctx.guild.roles,name="Systema")
            everyone = ctx.guild.default_role
            star = await ctx.guild.create_text_channel("starboard")
            await star.set_permissions(everyone,send_messages=False)
            await star.set_permissions(role,send_messages=True)
            await ctx.send("Successfully created starboard!")
    
    @commands.command()
    async def render(self,ctx,world):
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
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def init_suggest(self,ctx):
        pattern = r".*suggestion.*"
        already_have = None
        for i in ctx.guild.text_channels:
            if re.match(pattern,i.name,re.IGNORECASE):
                await ctx.send("Already have Suggestion channel!")
            else:
                already_have = True
        if not already_have:
            async with ctx.channel.typing():
                everyone = ctx.guild.default_role
                role = get(ctx.guild.roles,name="Systema")
                channel = await ctx.guild.create_text_channel("suggestion")
                await channel.set_permissions(everyone,send_messages=False)
                await channel.set_permissions(role,send_messages=True)
                await ctx.send("Successfully created!")
    
    @commands.command()
    async def rule34(self,ctx,tags):
        session = aiohttp.ClientSession()
        msg = await ctx.send("Please wait while im fetching.....")
        if ctx.channel.is_nsfw() or ctx.channel.name == "nsfw-not":
            yeah = False
            async with ctx.channel.typing():
                card = Embed(
                    	title="nsfw.png"
                    	)
                tags = tags.replace(" ","_")
                async with session.get(f"https://r34-json-api.herokuapp.com/posts?tags={tags}") as r:
                    data = await r.json()
                    if len(data) == 0:
                    	pass
                    else:
                    	yeah = True
                    	data = random.choice(data)
                    	card.set_image(url=data["file_url"])
            if yeah:
                await msg.edit(embed=card,content=None)
            else:
                await msg.edit(content="Either that tag doesn't exists or the connection is having an issue")
            await session.close()  
            await ctx.send("Just making sure if your 18+ 👀")
        else:
            await msg.edit(content="Not in nsfw channel!")
            await session.close()
            
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
    async def purge(self,ctx,amount:int=5,member:discord.Member=None):
        def check(m):
            discri = None
            if member is None:
                pass
            else:
                discri = member.name
            if m.pinned:
                return False
            elif m.author.name == discri:
                return True
            else:
                return True
        async with ctx.channel.typing():
            await asyncio.sleep(0.5)
            deleted = await ctx.channel.purge(limit=amount+1,check=check)
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
        okokok = False
        for i in ctx.guild.text_channels:
            if re.match(r".*suggestion.*",i.name,re.IGNORECASE):
                okokok = True
        
        if okokok:
            await ctx.message.delete()
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
                channel = None
                pattern = r".*suggestion.*"
                for i in ctx.guild.text_channels:
                    if re.match(pattern,i.name,re.IGNORECASE):
                        channel = i
                    
                suggest = await channel.send(embed=card)
                await suggest.add_reaction("✅")
                await suggest.add_reaction("❎")
                await ctx.send("Suggestion posted!")
        else:
            await ctx.send("Dont have Suggestion channel please use init_suggest")
    
    @commands.command()
    async def say(self,ctx,*,message):
            await ctx.send(message)
    
    @commands.command(aliases=["gay"])
    async def gayness(self,ctx,*,who):
            if len(who) > 100:
                await ctx.send("No spam word")
            else:
                who1 = int(str(sum([ord(i) for i in who]))[-2:])
                random.seed(int(who1))
                who1 = random.randint(0,200)
                if who.lower() in ["jabo","jabolesbo"]:
                    who1 = 0
                if who.lower() in ["saltydumpling","saltydumplings"]:
                    who1 = random.randint(1000,10000)
                card = Embed(
                title=f"{who1}% Gayness"
                )
                if who1 > 150:
                    card.description="VERY VERY GAY YOU ARE GAYESS OF THE GAY"
                elif who1 > 100:
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
                random.seed(0)
            
    @commands.command()
    @commands.is_owner()
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
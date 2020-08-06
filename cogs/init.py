from discord.ext import commands
from discord.ext import commands


class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def init(self, ctx):
        """
        Group commands init
        """
        card = Embed(
            title="Help for subcommands"
        )
        await ctx.send(embed=card)

    @init.command()
    @commands.has_permissions(manage_channels=True)
    async def starboard(self, ctx):
        """
        Initialize a Starboard channel
        """
        already = False
        pattern = r".*starboard.*"
        for i in ctx.guild.text_channels:
            if re.match(pattern, i.name, re.IGNORECASE):
                already = True
        if already:
            await ctx.send('Already have starboard!')
        if not already:
            role = get(ctx.guild.roles, name="Systema")
            everyone = ctx.guild.default_role
            star = await ctx.guild.create_text_channel("starboard")
            await star.set_permissions(everyone, send_messages=False)
            await star.set_permissions(role, send_messages=True)
            await ctx.send("Successfully created starboard!")

    @init.command()
    @commands.has_permissions(manage_channels=True)
    async def suggest(self, ctx):
        """
        Initialize a Suggestion channel
        """
        pattern = r".*suggestion.*"
        already_have = None
        for i in ctx.guild.text_channels:
            if re.match(pattern, i.name, re.IGNORECASE):
                await ctx.send("Already have Suggestion channel!")
                already_have = True
            else:
                already_have = False
        if not already_have:
            async with ctx.channel.typing():
                everyone = ctx.guild.default_role
                role = get(ctx.guild.roles, name="Systema")
                channel = await ctx.guild.create_text_channel("suggestion")
                await channel.set_permissions(everyone, send_messages=False)
                await channel.set_permissions(role, send_messages=True)
                await ctx.send("Successfully created!")
        else:
            await ctx.send("An error occurred :O")

    @init.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx):
        pass


def setup(bot):
    print("#Loaded init")
    bot.add_cog(Init(bot))

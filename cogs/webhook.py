import discord
from discord import Embed
from discord.ext import commands
from discord.utils import get


class Webhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook(self, ctx):
        """
        Group commands webhook
        """
        card = Embed(
            title="Help subcommands"
        )
        await ctx.send(embed=card)

    @webhook.command()
    @commands.has_permissions(manage_webhooks=True)
    async def create(self, ctx, name, channel: discord.TextChannel):
        """
        Creates a webhook
        """
        web = await channel.create_webhook(name=name)
        await ctx.send(web.url)

    @webhook.command()
    @commands.has_permissions(manage_webhooks=True)
    async def delete(self, ctx, channel: discord.TextChannel, name: str):
        """
        Delete webhook from channels
        """
        webs = await channel.webhooks()
        web = get(webs, name=name)
        if web:
            await web.delete()
            await ctx.send("Deleted!")
        else:
            await ctx.send("No names found")

    @webhook.command()
    @commands.has_permissions(manage_webhooks=True)
    async def url(self, ctx, channel: discord.TextChannel):
        """
        Shows payload url for webhook on channels
        """
        webs = await channel.webhooks()
        if not webs:
            await ctx.send("That channel doesn't have any webhooks")
        elif webs:
            card = Embed()
            for i in webs:
                card.add_field(name=i.name, value=i.url)
            await ctx.send(embed=card)


def setup(bot):
    print("#Loaded webhook")
    bot.add_cog(Webhook(bot))

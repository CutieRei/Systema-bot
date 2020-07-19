from discord.ext import commands
import discord
from discord import Embed,Colour
from datetime import datetime

def get_syntax(bot,cmd):
    for i in bot.commands:
        if i.name == cmd:
            cmd = i
            if i.signature == '':
                param = "No Parameters"
            else:
                param = i.signature
            if i.aliases == []:
                name = i.name
                return {"usage":f"[{name}]","param":param,"desc":i.description}
            elif i.aliases != []:
                alias = "|".join([str(i.name),*i.aliases])
                if i.help:
                    help = i.help
                else:
                    help = "no description"
                return {"usage":f"[{alias}]","param":param,"desc":help}

class Help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(aliases=["halp"])
    async def help(self,ctx,cmd=None):
        halp = f"Use {ctx.prefix}help [command] for info about specific command"
        """
        Shows this help!
        """
        if cmd is None:
            cmds = [i.name for i in self.bot.commands]
            card = Embed(
            title="Help command(Alpha)",
            colour=Colour.from_rgb(0,180,255),
            description=f'`{",".join(cmds)}`',
            timestamp=datetime.utcnow()
            )
            card.set_footer(icon_url=ctx.author.avatar_url_as(static_format='png'),text=halp)
            await ctx.send(embed=card)
        elif cmd.lower() in [i.name.lower() for i in self.bot.commands]:
            for i in self.bot.commands:
                if i.name.lower() == cmd.lower():
                    final_cmd = i
            info = get_syntax(self.bot,cmd)
            card = Embed(
            title=f"Help command(Alpha)",
            timestamp=datetime.utcnow()
            )
            if info["param"] == "No Parameters":
                card.add_field(name=f"```{info['usage']}```",value=info["desc"] or "No Description")
            else:
                card.add_field(name=f"```{info['usage']} {info['param']}```",value=info["desc"] or "No Description")
            card.set_footer(icon_url=self.bot.user.avatar_url_as(static_format='png'),text=halp)
            card.add_field(name="Cogs/Category",value=final_cmd.cog_name or "Not Categorized")
            await ctx.send(embed=card)
        else:
            await ctx.send("That command doesn't exist")
            

            
def setup(bot):
    print("#Loaded help")
    bot.add_cog(Help(bot))  
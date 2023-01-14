import datetime
import json

from funcs import config
from discord.ext import commands
import discord


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xe29124
        self.logo = "https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                    "?width=670&height=670"

    @commands.command()
    async def configmessage(self, ctx, arg, *, message):
        if arg == "invites":
            with open("config.json", "r") as f:
                conf = json.load(f)

            conf["invite_message"] = message

            with open("config.json", "w") as f:
                json.dump(conf, f, indent=4)

            await ctx.send("**Message modifié !**")

    @commands.Cog.listener()
    async def on_message(self, message):

        with open('config.json', 'r') as f:
            con = json.load(f)

        channel = self.bot.get_channel(con['suggestion'])  # ici tu mets le salon ou tu veux mettre tes sugg
        bot = message.guild.get_member(self.bot.user.id)
        if message.channel != channel:
            pass
        else:
            if message.author != bot:
                green = discord.utils.get(message.guild.emojis, name="tickgreen")
                red = discord.utils.get(message.guild.emojis, name="tickred")
                await message.delete()
                embed = discord.Embed(title=f"Nouvelle Suggestion :\n"
                                            f"{message.author}",
                                      color=self.color,
                                      description=f"**・** {message.content}")
                embed.set_footer(text=f"ArdenBot",
                                 icon_url=self.logo)
                embed.timestamp = datetime.datetime.utcnow()
                m = await channel.send(embed=embed)
                await m.add_reaction(green)
                await m.add_reaction(red)
            else:
                pass


def setup(bot):
    bot.add_cog(Commands(bot))

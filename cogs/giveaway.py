import datetime

import discord
from discord.ext import commands
import asyncio
import random

from funcs import convert


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xe29124
        self.logo = "https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                    "?width=670&height=670"

    @commands.command()
    async def gstart(self, ctx):
        await ctx.send("**Giveaway commencé ! Veuillez répondre aux question suivantes:**")
        questions = ["Quel salon choisir pour mettre le giveaway en place ?",
                     "Quel serait la durée du giveaway? (s|m|h|d)",
                     "Quel serait le lot du giveaway ?"]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(f"**+{'-'*(len(i)+5)}+**")
            await ctx.send(f"**{i}**")
            await ctx.send(f"**+{'-'*(len(i)+5)}+**")
            try:
                msg = await self.bot.wait_for('message', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Vous avez mis trop de temps pour répondre.')

            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(
                "Vous n'avez pas mentionné le salon correctement faites le comme {}".format(ctx.channel.mention))
            return

        channel = self.bot.get_channel(c_id)

        time = convert(answers[1])
        if time == -1:
            await ctx.send("Vous n'avez pas préciser la bonne unité de temps (s|m|d|h)")
            return
        elif time == -2:
            await ctx.send("Votre valeur de temps doit etre un entier.")
            return

        prize = answers[2]
        await ctx.send(f"Le giveaway va être dans {channel.mention} et prendra fin dans {answers[1]}")
        await channel.send("**🎉 GIVEAWAY 🎉**")
        embed = discord.Embed(title=prize, color=self.color,
                              description=f"Hôte: {ctx.author.mention}\n"
                                          f"**Réagissez avec l'émoji 🎉 pour participer au giveaway.**",
                              colour=self.color)
        embed.set_footer(text="ArdenBot", icon_url=self.logo)
        embed.timestamp = datetime.datetime.utcnow()
        mymsg = await channel.send(embed=embed)
        await mymsg.add_reaction("🎉")
        await asyncio.sleep(time[0])
        new_msg = await channel.fetch_message(mymsg.id)
        users = await new_msg.reactions[0].users().flatten()
        winner = random.choice(users)
        em = discord.Embed(title=prize, color=self.color,
                           description=f"Hôte: {ctx.author.mention}\n\n"
                                       f"Gagnant: {winner.mention}")
        em.set_footer(text="Giveaway terminé", icon_url=self.logo)
        em.timestamp = datetime.datetime.utcnow()
        await mymsg.edit(embed=em)
        await channel.send(f"**Félicitations** {winner.mention} vous avez gagné **{prize}.** 🎉")


def setup(bot):
    bot.add_cog(Giveaways(bot))

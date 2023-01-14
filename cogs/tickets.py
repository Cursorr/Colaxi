import asyncio

import discord
from discord.ext import commands

import json
import datetime
import chat_exporter
import io


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xe29124
        self.logo = "https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                    "?width=670&height=670"

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        emojis = ["🗡️", "⛏️", "🛒", "🎥", "🟧"]
        embed = discord.Embed(title="🏷️ Système de Ticket", color=self.color,
                              description="Pour que le staff puisse vous venir en aides,\n"
                                          "Veuillez réagir avec l’émoji correspondant à votre demande.\n\n"
                                          "**🗡️ Problème Modération**\n"
                                          "**⛏️ Problème Développement**\n"
                                          "**🛒 Problème Boutique**\n"
                                          "**🎥 Demande de partenariat**\n"
                                          "**🟧 Autre**")
        embed.set_footer(icon_url="https://media.discordapp.net/attachments/818148686335836191/819680219409285150/icon.png.png",
                         text="Copyright ©️ 2021 ArdenFaction - Tous droits réservés.")
        msg = await ctx.send(embed=embed)
        for e in emojis:
            await msg.add_reaction(e)

        with open("storage/tickets.json", "r") as f:
            config = json.load(f)

            config["ticket_msg"] = msg.id

        with open("storage/tickets.json", "w") as f:
            json.dump(config, f, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member
        emoji = payload.emoji

        emojis = {"🗡️": "mod", "⛏️": "dev", "🛒": "shop", "🎥": "partenariat", "🟧": "autre"}

        with open("storage/tickets.json", "r") as f:
            conf = json.load(f)

        i = 0

        for d in conf["cat"]:
            cat = discord.utils.get(member.guild.categories, id=d)
            for chan in cat.channels:
                if member.name.lower() in chan.name:
                    i += 1
                else:
                    continue


        if payload.message_id == conf["ticket_msg"] and str(emoji) in emojis.keys() and i == 0:

            channel = self.bot.get_channel(payload.channel_id)
            m = await channel.fetch_message(payload.message_id)
            await m.remove_reaction(emoji, member)
            public_role = discord.utils.get(member.guild.roles, id=conf["public_role"])
            category = discord.utils.get(member.guild.categories, id=conf[str(emoji)])
            await category.set_permissions(public_role, read_messages=False)
            new_ticket = await member.guild.create_text_channel(f"Ticket {emojis[str(emoji)]} {member.name}",
                                                                category=category)
            await new_ticket.set_permissions(member, read_messages=True)

            for role in conf["auth_role"]:
                discord_role = member.guild.get_role(role)
                await new_ticket.set_permissions(discord_role, read_message=True)

            mention = await new_ticket.send(member.mention)
            await mention.delete()
            embed = discord.Embed(title=f"✸ | ArdenTicket", color=self.color,
                                  description=f"Vous avez  créer un ticket, un membre du staff va "
                                              f"vous répondre dans les plus brefs délais.")
            embed.set_footer(text="Copyright ©️ 2021 Ardenfaction - Tous droits réservés.",
                             icon_url="https://media.discordapp.net/attachments/818148686335836"
                                      "191/819680219409285150/icon.png.png")
            embed.timestamp = datetime.datetime.utcnow()
            await new_ticket.send(embed=embed)
            msg = []
            for staff in conf['staff_mention']:
                staff_role = discord.utils.get(member.guild.roles, id=staff)
                msg.append(staff_role.mention)

            await new_ticket.send(" ".join(msg))
            conf["list"].append(new_ticket.id)

        else:
            pass

        with open("storage/tickets.json", "w") as f:
            json.dump(conf, f, indent=4)


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def close(self, ctx):
        with open("storage/tickets.json", "r") as f:
            tickets = json.load(f)

        if ctx.channel.id in tickets["list"]:

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

            try:
                em = discord.Embed(title="ArdenTicket",
                                   description="Etes vous sûr de fermer ce ticket ? Répondez "
                                               "par `close` si vous l'êtes.",
                                   color=self.color)
                await ctx.send(embed=em)
                await self.bot.wait_for("message", check=check, timeout=30)
                await ctx.send("**Patientez...**")
                x = ctx.channel.name.split("-")
                y = x[2].capitalize()
                transcript = await chat_exporter.export(ctx.channel)
                transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"Transcript-{y}-{x[1].capitalize()}.html")
                log_channel = self.bot.get_channel(819912735974359050)
                tr = discord.Embed(color=self.color)
                tr.add_field(name="Ticket de", value=y, inline=False)
                tr.add_field(name="Fermé par", value=ctx.author.mention, inline=False)
                tr.add_field(name="Nom du ticket", value=ctx.channel.name, inline=False)
                await log_channel.send(embed=tr, file=transcript_file)
                fermeture = discord.Embed(title="Fermeture du ticket", color=self.color,
                                          description="Ce ticket va se supprimer dans 5 secondes...")
                await ctx.channel.send(embed=fermeture)
                await asyncio.sleep(5)
                await ctx.channel.delete()
            except asyncio.TimeoutError:
                em = discord.Embed(title="ArdenTicket",
                                   description="Vous avez mis trop de temps pour fermer ce ticket, veuillez réesseayer.",
                                   color=self.color)
                await ctx.send(embed=em)

        else:
            pass


def setup(bot):
    bot.add_cog(Tickets(bot))

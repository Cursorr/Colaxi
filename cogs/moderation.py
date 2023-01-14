import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from funcs import convert


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xe29124
        self.logo = "https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                    "?width=670&height=670"

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason="Aucune Raison"):
        print(member.top_role)
        print((ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner) and member != ctx.guild.owner)
        if (ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner) and member != ctx.guild.owner:
            print(1)
            await member.ban()
            embed = discord.Embed(color=self.color)
            embed.add_field(name="**Modérateur:**", value=ctx.author.mention, inline=False)
            embed.add_field(name="**Membre banni:**", value=member.mention, inline=False)
            embed.add_field(name="**Raison:**", value=reason, inline=False)
            embed.set_footer(text="ArdenBot", icon_url=self.logo)
            embed.timestamp = datetime.utcnow()
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)
            embed.set_thumbnail(url=self.logo)
            await ctx.send(embed=embed)

        else:
            await ctx.send(embed=discord.Embed(description="**Mauvaise Utilisation**\nVeuillez utiliser la commande `!ban <membre> <raison>`", color=self.color))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, t, reason="Aucune Raison"):
        guild = ctx.guild
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if (ctx.author.top_role > member.top_role or ctx.author == ctx.guild.owner) and member != ctx.guild.owner:
            if not role:
                try:
                    muted = await ctx.guild.create_role(name="Muted", reason="Pour pouvoir Mute")
                    for c in ctx.guild.channels:
                        await c.set_permissions(muted, send_messages=False)
                except discord.Forbidden:
                    return await ctx.send(embed=discord.Embed(description=f"Je n'ai pas la permission de mute.", color=self.color))
                if role in member.roles:
                    await ctx.send(embed=discord.Embed(description=f"{member} est déjà mute.", color=self.color))

                else:

                    d = convert(t)
                    print(d)
                    val = int(t[:-1])
                    embed = discord.Embed(colour=self.color)
                    embed.add_field(name=f"**Modérateur**", value=ctx.author.mention, inline=False)
                    embed.add_field(name=f"**Membre Mute**", value=member.mention, inline=False)
                    embed.add_field(name=f"**Durée**", value=f'{val} {d[1]}', inline=False)
                    embed.add_field(name=f"**Raison**", value=reason, inline=False)
                    embed.set_footer(text="ArdenBot", icon_url=self.logo)
                    embed.timestamp = datetime.utcnow()
                    embed.set_author(name=member.name, icon_url=member.avatar_url)
                    embed.set_thumbnail(url=self.logo)
                    await ctx.send(embed=embed)
                    await member.add_roles(role)
                    await asyncio.sleep(d[0])
                    await member.remove_roles(role)
            else:
                if role in member.roles:
                    await ctx.send(embed=discord.Embed(description=f"{member} est déjà mute", color=self.color))
                else:
                    d = convert(t)
                    print(d)
                    val = int(t[:-1])
                    embed = discord.Embed(colour=self.color)
                    embed.add_field(name=f"**Modérateur**", value=ctx.author.mention, inline=False)
                    embed.add_field(name=f"**Membre Mute**", value=member.mention, inline=False)
                    embed.add_field(name=f"**Durée**", value=f'{val} {d[1]}', inline=False)
                    embed.add_field(name=f"**Raison**", value=reason, inline=False)
                    embed.set_footer(text="ArdenBot", icon_url=self.logo)
                    embed.timestamp = datetime.utcnow()
                    embed.set_author(name=member.name, icon_url=member.avatar_url)
                    embed.set_thumbnail(url=self.logo)
                    await ctx.send(embed=embed)
                    await member.add_roles(role)
                    await asyncio.sleep(d[0])
                    await member.remove_roles(role)

        else:
            await ctx.send(embed=discord.Embed(description=f"**Vous n'avez pas la permission de mute ce membre.**", color=self.color))


def setup(bot):
    bot.add_cog(Moderation(bot))

import datetime
import heapq
import json
import operator

from funcs import config, my_format
from discord.ext import commands
import discord


def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xe29124
        self.logo = "https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                    "?width=670&height=670"
        self.invites = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = {i.id: i for i in await guild.invites()}
            except Exception as exception:
                print(exception)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.invites[guild.id] = {i.id: i for i in await guild.invites()}

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id in self.bot.invites:
            self.invites[guild_id][invite.id] = invite
        else:
            self.invites[guild_id] = {i.id: i for i in await invite.guild.invites()}

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id in self.invites:
            try:
                del self.invites[guild_id][invite.id]
            except KeyError:
                return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild: discord.Guild = member.guild
        
        if member.bot:
            return

        try:
            before_invites = self.bot.invites[guild.id]
            actual_invites = await guild.invites()
        
        except Exception as exception:
            print(exception)


        if actual_invites and before_invites:
            invite = self.find_invite(before_invites, actual_invites)
            if invite:
                
                with open("storage/invites.json", "r") as f:
                    users = json.load(f)
                    inviter = invite.inviter.id

                    if f'{inviter}' not in users:
                        users[f'{inviter}'] = {}
                        users[f'{inviter}']["l"] = 0
                        users[f'{inviter}']["b"] = 0
                        users[f'{inviter}']["m"] = []

                    else:
                        users[f'{inviter}']["m"].append(member.id)

                with open("storage/invites.json", "w") as f:
                    json.dump(users, f, indent=4)
                conf = config()
                channel = self.bot.get_channel(conf["invite_channel"])
                await channel.send(my_format(conf["invite_message"], member_mention=member.mention,
                                             member=member,
                                             inviter=invite.inviter,
                                             inviter_mention=invite.inviter.mention,
                                             invites=len(users[f'{inviter}']['m'])))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_id = member.id

        if member.bot:
            return

        with open("storage/invites.json", "r") as f:
            data = json.load(f)

        for k, v in data.items():
            for m in v["m"]:
                if member_id == m:
                    data[f'{k}']["m"].remove(member_id)
                    with open("storage/invites.json", "w") as f:
                        json.dump(data, f, indent=4)
                        inviter = k

        with open("storage/invites.json", "r") as f:
            users = json.load(f)

            users[f'{inviter}']['l'] += 1

        with open("storage/invites.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command(aliases=["invites"])
    async def invite(self, ctx, member: discord.Member = None):
        with open("storage/invites.json", "r") as f:
            users = json.load(f)
        if member is None:
            x = users[f"{ctx.author.id}"]

            em = discord.Embed(title=f"{ctx.author.name}", color=self.color, description=f"Vous avez **{len(x['m'])}** invites. "
                                                                               f"(**{x['l'] + x['b'] + len(x['m'])}** "
                                                                               f"ordinaires, **{x['l']}** partis et "
                                                                               f"**{x['b']}** bonus.)")
            em.timestamp = datetime.datetime.utcnow()
            em.set_footer(icon_url=self.logo, text="Arden Bot Invites")
            await ctx.send(embed=em)

        if member is not None:
            m = []
            for k, v in users.items():
                m.append(k)

            if str(member.id) in m:
                x = users[f"{member.id}"]

                em = discord.Embed(title=f"{member.display_name}", color=self.color,
                                   description=f"{member} a **{len(x['m'])}** invites. "
                                               f"(**{x['l'] + x['b'] + len(x['m'])}** "
                                               f"ordinaires, **{x['l']}** partis et "
                                               f"**{x['b']}** bonus.)")
                em.timestamp = datetime.datetime.utcnow()
                em.set_footer(icon_url=self.logo, text="Arden Bot Invites")
                await ctx.send(embed=em)
            else:
                embed = discord.Embed(title=f"{member}", color=self.color,
                                      description=f"{member} a **0** invites. "
                                                  f"(**0** "
                                                  f"ordinaires, **0** partis et "
                                                  f"**0** bonus.)")
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(icon_url=self.logo, text="Arden Bot Invites")
                await ctx.send(embed=embed)

    @commands.command()
    async def top_invite(self, ctx):
        mess = []
        with open("storage/invites.json", "r") as f:
            users = json.load(f)
            l = [(k, len(v["m"]), v['l'], v['b']) for k, v in users.items()]
        word = heapq.nlargest(5, l, key=operator.itemgetter(1))

        if len(users) <= 5:

            for i in range(1, len(users) + 1):
                mess.append(
                    f"**{i} -** <@{word[i - 1][0]}> • **{word[i - 1][1]}** invites. "
                    f"(**{word[i - 1][1] + word[i - 1][2]}** ordinaires, "
                    f"**{word[i - 1][2]}** partis, **{word[i - 1][3]}** bonus).\n")
            m = ''.join(mess)

        else:
            for i in range(1, 6):
                mess.append(
                    f"**{i} -** <@{word[i - 1][0]}> • **{word[i - 1][1]}** invites. "
                    f"(**{word[i - 1][1] + word[i - 1][2]}** ordinaires, "
                    f"**{word[i - 1][2]}** partis, **{word[i - 1][3]}** bonus).\n")
            m = ''.join(mess)

        embed = discord.Embed(title="Classement invites", color=self.color, description=m)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(icon_url=self.logo, text="Arden Bot Invites")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addbonus(self, ctx, member: discord.Member, n: int):
        with open("storage/invites.json", "r") as f:
            users = json.load(f)

        u = []
        for k, v in users.items():
            u.append(k)

        if str(member.id) in u:
            users[str(member.id)]["b"] += n
        else:
            users[f'{member.id}'] = {}
            users[f'{member.id}']["l"] = 0
            users[f'{member.id}']["b"] = n
            users[f'{member.id}']["m"] = []

        with open("storage/invites.json", "w") as f:
            json.dump(users, f, indent=4)

        await ctx.send(embed=discord.Embed(description=f"**{n}** invitations bonus ont été"
                                                       f" ajoutés à **{member.display_name}.**",
                                           title="AddBonus",
                                           color=self.color))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removebonus(self, ctx, member: discord.Member, n: int):
        with open("storage/invites.json", "r") as f:
            users = json.load(f)

        u = []
        for k, v in users.items():
            u.append(k)

        if str(member.id) in u:
            if users[str(member.id)]["b"] == 0:
                await ctx.send(embed=discord.Embed(description=f"**{member.display_name} a 0 invitation bonus.**", color=self.color))

            elif users[str(member.id)]["b"] >= n:
                users[str(member.id)]["b"] -= n
                await ctx.send(embed=discord.Embed(description=f"**{n}** invitations bonus ont été"
                                                               f" retirés de **{member.display_name}.**",
                                                   title="Ajout bonus",
                                                   color=self.color))
            else:
                await ctx.send(embed=discord.Embed(description=f'**Veuillez mettre un nombre inférieur ou égal à {users[str(member.id)]["b"]} (le bonus de {member.display_name}).**', title="AddBonus", color=self.color))
        else:
            await ctx.send(embed=discord.Embed(description=f"**{member.display_name} a 0 invitation bonus.**", color=self.color))

        with open("storage/invites.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Vous n'avez pas la permission d'executer cette commande.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Mauvais utilisation. `!help`")


def setup(bot):
    bot.add_cog(Invites(bot))

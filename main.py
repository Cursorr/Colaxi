import asyncio
import datetime
import json
from mcstatus import JavaServer
import discord
from discord.ext import commands, tasks
from funcs import config

from itertools import cycle

status = cycle(["{member} Membres", "{connected} Connectés"])

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

Extensions = [
    "invites",
    "giveaway",
    "tickets",
    "commands",
    "moderation"
]

config = config()

@bot.event
async def on_ready():
    print("Bot connecté")
    member_count.start()


@bot.command()
@commands.has_permissions(administrator=True)
async def annonce(ctx):
    await ctx.send("**__Salut__, votre meilleur bot est au service !** \n **Veuillez remplir ce questionnaire pour que "
                   "tout soit parfait. Vous avez jusqu'à 15 minutes pour répondre à tout.**\n Commençons !")

    questions = ["Quel salon choisir pour cette annonce ?",
                 "Quelle est le titre de cette annonce ?",
                 "Quelle est votre message d'annonce ?"]

    answers = []

    await asyncio.sleep(3)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send("**|----------------------------------------------------|**")
        await ctx.send(i)
        await ctx.send("**|----------------------------------------------------|**")

        try:
            msg = await bot.wait_for('message', timeout=60*15, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Vous avez mis +15m pour répondre, soyez plus vif la prochaine fois.')

        else:
            answers.append(msg.content)

    try:
        c_id = int(answers[0][2:-1])

    except:
        await ctx.send("Vous n'avez pas mentionné le salon correctement. Faites le comme {}".format(ctx.channel.mention))
        return

    channel = bot.get_channel(c_id)

    embed = discord.Embed(title=answers[1], color=0xe29124, description=answers[2])
    embed.set_footer(text="ArdenBot Annonces", icon_url="https://media.discordapp.net/attachments/818148686335836191/818161492410892338/Mascotte.png" \
                                                        "?width=670&height=670")
    embed.timestamp = datetime.datetime.utcnow()

    await channel.send(embed=embed)


@annonce.error
async def annonce_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        msg = await ctx.send("Vous n'avez pas la permissions d'executer cette commande.")
        await asyncio.sleep(4)
        await msg.delete()

@tasks.loop(seconds=5)
async def member_count():
    var = next(status)
    with open('config.json', 'r') as f:
        config = json.load(f)

    server = JavaServer.lookup(config["ip_adress"])
    online = server.status().players.online
    guild = bot.get_guild(config["guild_id"])

    await bot.change_presence(activity=discord.Game(name=var.format(
        member=guild.member_count, connected=online)))

for extention in Extensions:
    bot.load_extension(f"cogs.{extention}")

bot.run(config["token"])

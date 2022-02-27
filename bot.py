from ast import Lambda
from http import client, server
import discord
from discord.ext import commands, tasks
import youtube_dl
import asyncio
from random import choice
import json
import os

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Prefix": "."}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]
prefix = configData["Prefix"]


activity = discord.Activity(type=discord.ActivityType.listening, name="You")

bot = commands.Bot(command_prefix=".", activity=activity, status=discord.Status.idle)

bot.remove_command("help")

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



@bot.event
async def on_ready():
    print("Bot is Ready")


@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000, 1)
    await ctx.send(f"Pong! {latency}ms")

@bot.command()
async def hi(ctx, member):
    await ctx.send(f"Hello! {member}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, * , reason = None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} was banned!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, * , reason = None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} was kicked!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = member.split('#')

    for ban in bannedUsers:
        user = ban.user

        if(user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} was unbanned!")
            return


@bot.command()
async def userinfo(ctx):
    user = ctx.author

    embed = discord.Embed(title = "USER INFO", description = f"The info I retrived about {user}", color = user.color)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="NAME", value=user.name, inline=True)
    embed.add_field(name="NICKNAME", value=user.nick, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="STATUS", value=user.status, inline=True)
    embed.add_field(name="TOP ROLE", value=user.top_role.name, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):   
    embed = discord.Embed(title="HELP")
    embed.add_field(name="Ping", value="Gets the bot latency", inline=True)
    embed.add_field(name="Hi", value="Greets the user" ,inline=True)
    embed.add_field(name="Userinfo", value="Retreives the info of the user", inline=True)
    embed.add_field(name="Kick", value="Kicks the user", inline=True)
    embed.add_field(name="Ban", value="Bans the user", inline=True)
    embed.add_field(name="Unban", value="Unbans the user", inline=True)
    
    await ctx.message.delete()
    await ctx.author.send(embed=embed)

@bot.command()
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel!")
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
    await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(player, after=lambda e:print('Player Error: %s' %e) if e else None)
    
    await ctx.send(f'**Now Playing:** {player.title}')
@bot.command()
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()










# To do:
# custimize the embed links
# Add music functionality
bot.run(token)
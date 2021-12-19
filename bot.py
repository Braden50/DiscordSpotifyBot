from __future__ import unicode_literals

from discord.utils import get
from discord import FFmpegPCMAudio
import discord
from discord.ext import commands,tasks
import os
# import youtube_dl
import yt_dlp as youtube_dl
# from appSecrets import discord_key
import urllib.request
import re
import random
import asyncio
import requests

from spotify import Spotify
import time

    
import secrets

spotify_objects = {}   # one for each user {userid:spotify}

# sp.initialize()
# # sp.printUser()
# os.environ['DISCORD_TOKEN'] = 'token'
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
if DISCORD_TOKEN is None:
    raise Exception("No discord token provided")
elif DISCORD_TOKEN == 'token':
    raise Exception("token is tokeN")

players = {}  # TODO: carry different players per channel
play_next_song = asyncio.Event()
songs = asyncio.Queue()

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$$',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '/tmp/%(title)s.mp3'
}


ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# class YTDLSource(discord.PCMVolumeTransformer):
#     def __init__(self, source, *, data, volume=0.5):
#         super().__init__(source, volume)
#         self.data = data
#         self.title = data.get('title')
#         self.url = ""

#     @classmethod
#     async def from_url(cls, url, *, loop=None, stream=False):
#         loop = loop or asyncio.get_event_loop()
#         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
#         if 'entries' in data:
#             # take first item from a playlist
#             data = data['entries'][0]
#         filename = data['title'] if stream else ytdl.prepare_filename(data)
#         return filename


async def audio_player_task():
    while True:
        print("A" * 20)
        play_next_song.clear()
        current = await songs.get()
        if current['voice'].is_playing():
            current['voice'].stop()
        current['voice'].play(current['player'])
        await play_next_song.wait()

def toggle_next():
    print("B" * 20)
    client.loop.call_soon_threadsafe(play_next_song.set)


def search(query):
    '''
    Returns a url to the first youtube video that comes up when searching with the query
    '''
    query = query.replace(" ", '+')
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    url = "https://www.youtube.com/watch?v=" + video_ids[0]
    return url
    

def getGuck():
    case = [str.upper, str.lower]
    guck_string = ""
    for i in range(random.randint(20, 100)):
        guck = "".join(random.choice(case)(c) for c in "guck")
        guck_string += (guck)
    return guck_string


def getName(ctx):
    username = ctx.message.author.name
    if username =="Braden50":
        return random.choice(["Sensei", "Daddy", "Senpai", "Big Daddy B", "Ass Clapper",
                              "xXo Silly oXx", "Everlasting Light"])
    return username


async def greeting(ctx):
    await ctx.send(f'Anything for you {getName(ctx)} uWu')


@bot.command(name='guck', help='Guck command for fun')
async def sucker(ctx):
    await greeting(ctx)
    guck_string = getGuck
    await ctx.send(getGuck())


@bot.command(name='authSpotify', help='Connects to spotify')
async def authSpotify(ctx):
    s = Spotify()
    user_id = ctx.message.author.id
    spotify_objects[user_id] = s
    await ctx.send(f'Authenticate Spotify here: {s.getAuthUrl()}. Follow sign-on instructions and once provided the key, execute: $$connectSpotify <key>')



@bot.command(name='connectSpotify', help='Connects to spotify')
async def connectSpotify(ctx, key):
    user_id = ctx.message.author.id
    if user_id not in spotify_objects:
        await ctx.send('Error: First, you need to sign in and get a specialized access key by using "authSpotify" command')
        return
    # try:
    url_with_token = requests.get(f"{website_url}token?key={key}").text
    # except:
    #     print("connectSpotify: Key Error")
    s = spotify_objects[user_id]   # not checking if token needs refresh
    spotify_name = s.authenticate(url_with_token)
    await ctx.send(f"Welcome {spotify_name}! Your spotify has been connected!")



@bot.command(name='spotify', help='Connects to spotify')
async def spotifyCommands(ctx, command, **args):
    user_id = ctx.message.author.id
    if user_id not in spotify_objects:
        await ctx.send('Error: You need to sign into your spotify first with "authSpotify" then "connectSpotify <key>"')
        return
    s = spotify_objects[user_id]
    if command.lower() == "now":
        await playNow(ctx, s)
    else:
        await ctx.send('Spotify command not implemented')
    # TODO: check if token is still good
    

    
# TODO
@bot.command(help='"$$spotify now" - Plays the current spotify playing song on the discord')
async def playNow(ctx, s):
    auth_url = s.getAuthUrl()
    name = s.authenticate(auth_url)
    cs = s.sp.currently_playing()   # "current song"
    if cs is None or cs['is_playing'] is False:
        await ctx.send('Nothing is currently playing SILLY.')
        return
    
    album = cs['item']['album']['name']
    artist = cs['item']['artists'][0]['name']
    song_name = cs['item']['name']
    query = f"{song_name} by {artist} on {album}"
    await play(ctx, single_query=query)



@bot.command(name='play', help='To play song')
async def play(ctx, *args, single_query=None):
    await greeting(ctx)
    if len(args) == 0 and single_query is None:
        voice_client = ctx.message.guild.voice_client
        if not voice_client:
            await ctx.send(f'Nothing is ready to play, give me something to search silly!')
        else:
            if voice_client.is_playing():
                await ctx.send(f'Something is already playing {getName(ctx)}, give me something to search.')
            else:
                await ctx.send(f"You didn't give me anything to search... did you mean \"resume\"?")
        return

    if single_query:
        query = single_query
    else:
        query = " ".join(args)    
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice is None:  # Voice client needs to be initialized and connected to play music
        if not voice.is_connected():
            await channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    else:
        await channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    # NUM_ATTEMPTS = 5
    # for attempt in range(NUM_ATTEMPTS):
    try:
        url = search(query)   # replace spaces with + for url search query
        channel = ctx.message.author.voice.channel
    except Exception as e:
        print(1, e)
    try:
        print(url)
        info = ytdl.extract_info(url, download=False)
        print("EXTRACTED")
        extracted_url = info['formats'][0]['url']
        try:
            player = FFmpegPCMAudio(extracted_url, **ffmpeg_options)
        except Exception as e:
            print(69, e, e.args)
    except Exception as e:
        print(2, e)
    try:
        await songs.put({
            "voice": voice,
            "player": player})
        await ctx.send(f'Playing... eventually: {url}')
    except Exception as e:
        print(3, e)
    print("D" * 20)


@bot.command(name='skip', help='skip')
async def skip(ctx):
    if songs.qsize() == 0:
        await ctx.send("No more songs in the queue")
        return        
    toggle_next()


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("I am not playing anything at the moment.")
    

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("I am not playing anything before this.")
    


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        # await voice_client.stop()
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


# @bot.command(name='stop', help='Stops the song')
# async def stop(ctx):
#     voice_client = ctx.message.guild.voice_client
#     if voice_client.is_playing():
#         # await voice_client.stop()
#         voice_client.stop()
#     else:
#         await ctx.send("The bot is not playing anything at the moment.")


@bot.event
async def on_ready():
    print('Running!')
    for guild in bot.guilds:
        print('Active in {}\n Member Count : {}'.format(guild.name,guild.member_count))


@bot.command(help = "Prints details of Author")
async def whats_my_name(ctx) :
    await ctx.send('Hello {}'.format(ctx.author.name))

# @bot.command(help = "Prints details of Server")
# async def where_am_i(ctx):
#     owner=str(ctx.guild.owner)
#     region = str(ctx.guild.region)
#     guild_id = str(ctx.guild.id)
#     memberCount = str(ctx.guild.member_count)
#     icon = str(ctx.guild.icon_url)
#     desc=ctx.guild.description
    
#     embed = discord.Embed(
#         title=ctx.guild.name + " Server Information",
#         description=desc,
#         color=discord.Color.blue()
#     )
#     embed.set_thumbnail(url=icon)
#     embed.add_field(name="Owner", value=owner, inline=True)
#     embed.add_field(name="Server ID", value=guild_id, inline=True)
#     embed.add_field(name="Region", value=region, inline=True)
#     embed.add_field(name="Member Count", value=memberCount, inline=True)

#     await ctx.send(embed=embed)

#     members=[]
#     async for member in ctx.guild.fetch_members(limit=150) :
#         await ctx.send('Name : {}\t Status : {}\n Joined at {}'.format(member.display_name,str(member.status),str(member.joined_at)))


@bot.event
async def on_message(message) :
    '''
    Executes even if prefix isn't included in message
    '''
    # bot.process_commands(msg) is a couroutine that must be called here since we are overriding the on_message event
    await bot.process_commands(message) 
    if "tits" in message.content:
        await message.channel.send('nice')


def start():
    bot.loop.create_task(audio_player_task())
    bot.run(DISCORD_TOKEN)



if __name__ == "__main__" :
    # Assuming that if main is run it is local
    bot.loop.create_task(audio_player_task())
    bot.run(DISCORD_TOKEN)

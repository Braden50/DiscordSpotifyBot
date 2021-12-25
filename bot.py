import os
import discord
import datetime
import json
import util
import ui
import random
import requests
from music import Song, Playlist, PlayerInstance
from discord_slash import SlashCommand, SlashContext, ComponentContext
from discord_slash.model import SlashCommandOptionType

from spotify import Spotify
# print(discord.Intents().all())
client = discord.Client(intents=discord.Intents().all())
slash = SlashCommand(client, sync_commands=True)
guild_ids = {} #json.loads(os.environ.get('GUILD_IDS'))
players = {} # players: dict[int, PlayerInstance] = {}
spotify_objects = {}   # one for each user {userid:spotify}

SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
if SPOTIPY_REDIRECT_URI is None:
    raise Exception("No discord token provided")

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}#{client.user.discriminator}')
    print('Ready!')

async def connect_vc(ctx: SlashContext):
    voice_channel = ctx.author.voice.channel if ctx.author.voice is not None else None
    if voice_channel is None:
        return False

    if ctx.voice_client is not None and ctx.voice_client.is_connected():
        await ctx.voice_client.move_to(voice_channel)
    else:
        voice_client = await voice_channel.connect()
        players[voice_channel.id] = PlayerInstance(voice_client)
    return True

def get_player(ctx: SlashContext):
    if ctx.voice_client is None:
        return None

    vc_id = ctx.voice_client.channel.id
    if vc_id in players:
        return players[vc_id]
    return None

async def get_player_or_connect(ctx: SlashContext, *, reply=False):
    player = get_player(ctx)
    if player is None:
        if not await connect_vc(ctx):
            if reply:
                await ctx.send(content=ui.ERR_NOT_IN_VC)
            return None
        player = get_player(ctx)

    if player is None and reply:
        await ctx.send(content=ui.ERR_UNKNOWN)

    return player

@slash.component_callback()
async def handle_component(ctx: ComponentContext):
    pass


def getName(ctx: SlashContext):
    username = str(ctx.author)
    if username =="Braden50#7614":
        return random.choice(["Sensei", "Daddy", "Senpai", "Big Daddy B", "Ass Clapper",
                              "xXo Silly oXx", "Everlasting Light"])
    return username.split("#")[0]


async def kindResponse(ctx: SlashContext):
    await ctx.send(f'Anything for you {getName(ctx)} uWu')


@slash.slash(name="test",
             description="This is just a test command, nothing more.")
async def test(ctx):
  await ctx.send(content="Hello World!")


@slash.slash(
    name='join',
    description='Join the VC',
    guild_ids=guild_ids
)
async def join(ctx: SlashContext):
    if not await connect_vc(ctx):
        return await ctx.send(content=ui.ERR_NOT_IN_VC)

    await ctx.send(content=f'Hey {getName(ctx)}')

@slash.slash(
    name='leave',
    description='Leave the VC',
    guild_ids=guild_ids
)
async def leave(ctx: SlashContext):
    voice_channel = ctx.author.voice.channel if ctx.author.voice is not None else None
    if voice_channel is None:
        await ctx.send(content=ui.ERR_NOT_IN_VC)
        return

    await ctx.voice_client.disconnect(force=True)
    players[voice_channel.id] = None

    await ctx.send(content='Bye!')

@slash.slash(
    name='play',
    description='Add a song to the queue',
    options=[
        {
            'name': 'query',
            'description': 'YouTube video or playlist URL, search query, or queue number',
            'type': SlashCommandOptionType.STRING,
            'required': True
        }
    ],
    guild_ids=guild_ids
)
async def play(ctx: SlashContext, etc=None, *, query):
    await ctx.defer()
    await _play(ctx, query)

async def _play(ctx: SlashContext, etc=None, *, query, m_queries = None):
    # m_queries is a list of queries to add multiple songs via youtube search at a time
    if not m_queries or len(m_queries) < 1:  # if m_queries None or an empty list, default to query
        m_queries = [query]
            
    player = await get_player_or_connect(ctx, reply=True)
    if player is None:
        return

    requester_id = ctx.author_id
    queue_empty = len(player.playlist) == 0
    queue_ended = not player.playlist.has_next()

    # If query is a number, jump to that playlist index
    if query.isnumeric():
        player.playlist.jump(int(query) - 1, relative=False)

        if await player.play():
            await ctx.send(embed=await ui.now_playing(player))
        else:
            await ctx.send(content='End of queue')
        return

    songs = []
    if util.is_url(query):
        # Query is a URL, queue it
        songs = await player.queue_url(query, requester_id)
    else:
        # Search YouTube and get first result
        for temp_query in m_queries:
            search = await util.youtube_extract_info(f'ytsearch1:{temp_query}')
            results = list(search['entries'])
            url = 'https://youtu.be/' + results[0]['id']
            song = await player.queue_url(url, requester_id)
            songs.append(song)


    if len(songs) > 1:
        await ctx.send(
            content='{} songs queued'.format(len(songs))
        )
    elif len(songs) == 1:
        song = await ui.format_song(songs[0])
        await ctx.send(content=f'Queued: {song}')
    else:
        await ctx.send(content='No songs queued')


    # Don't disturb the player if it's already playing
    if player.is_playing():
        return

    # If the player is fresh, play
    if queue_empty:
        return await player.play()

    # If it isn't playing because it reached the end of the queue,
    # play the song that was just added to the queue
    if queue_ended:
        return await player.play_next()

    # Otherwise resume playback
    await player.resume()


@slash.slash(
    name='queue',
    description='Show the current queue',
    guild_ids=guild_ids
)
async def queue_list(ctx: SlashContext):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    await ctx.defer()

    embed = await ui.queue(player)
    await ctx.send(embed=embed)

@slash.slash(
    name='clear',
    description='Remove all songs from the current queue',
    guild_ids=guild_ids
)
async def queue_clear(ctx: SlashContext):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    await player.stop()
    player.playlist.clear()

    await ctx.send(content='Queue cleared!')

@slash.slash(
    name='shuffle',
    description='Shuffle the order of songs in the queue',
    guild_ids=guild_ids
)
async def queue_shuffle(ctx: SlashContext):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    player.playlist.shuffle()
    await ctx.send(content='Queue shuffled!')

@slash.slash(
    name='skip',
    description='Skip current song',
    options=[
        {
            'name': 'number',
            'description': 'How many songs to skip',
            'type': SlashCommandOptionType.INTEGER,
            'required': False
        }
    ],
    guild_ids=guild_ids
)
async def skip(ctx: SlashContext, *, number=1):
    await ctx.defer()
    player = await get_player_or_connect(ctx, reply=True)
    if player is None:
        return

    player.playlist.jump(number)

    if await player.play():
        await ctx.send(embed=await ui.now_playing(player))
    else:
        await ctx.send(content='End of queue')

@slash.slash(
    name='np',
    description='Show the currently playing song',
    guild_ids=guild_ids
)
async def now_playing(ctx: SlashContext):
    player = await get_player_or_connect(ctx, reply=True)
    if player is None:
        return

    await ctx.send(embed=await ui.now_playing(player))

@slash.slash(
    name='pause',
    description='Pause the current song',
    guild_ids=guild_ids
)
async def pause(ctx: SlashContext):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    if player.is_playing():
        await player.pause()

    await ctx.send(content='Paused')

@slash.slash(
    name='resume',
    description='Resume playback',
    guild_ids=guild_ids
)
async def resume(ctx: SlashContext):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    if not player.is_playing():
        await player.resume()

    await ctx.send(embed=await ui.now_playing(player))

@slash.slash(
    name='loop',
    description='Enable/disable looping',
    options=[
        {
            'name': 'mode',
            'description': 'Loop this song or the whole queue?',
            'type': SlashCommandOptionType.STRING,
            'required': True,
            'choices': [
                { 'name': 'disable', 'value': PlayerInstance.LOOP_NONE },
                { 'name': 'song', 'value': PlayerInstance.LOOP_SONG },
                { 'name': 'queue', 'value': PlayerInstance.LOOP_QUEUE }
            ]
        }
    ],
    guild_ids=guild_ids
)
async def loop(ctx: SlashContext, mode=PlayerInstance.LOOP_NONE):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    player.loop_mode = mode
    await ctx.send(content=f'Loop mode set to **{mode}**')

@slash.slash(
    name='remove',
    description='Remove a song from the queue',
    options=[
        {
            'name': 'number',
            'description': 'The queue number of the song to remove',
            'type': SlashCommandOptionType.INTEGER,
            'required': True
        }
    ],
    guild_ids=guild_ids
)
async def remove_song(ctx: SlashContext, number: int):
    player = get_player(ctx)
    if player is None:
        return await ctx.send(content=ui.ERR_NO_PLAYER)

    song = player.playlist.remove(number - 1)
    title = await song.get_title()
    url = song.url
    await ctx.send(content=f'Removed #{number} [{title}]({url})')

    if len(player.playlist) == 0:
        return await player.stop()

    if number - 1 == player.playlist.get_index():
        await player.play()


''' Spotify commmands '''


@slash.slash(
    name='auth_spotify',
    description='Connects to spotify',
    guild_ids=guild_ids
)
async def authSpotify(ctx: SlashContext):
    await ctx.defer()
    print("Attempting to authenticate")
    s = Spotify()
    # user_id = str(ctx.author)
    user_id = str(ctx.author_id)
    spotify_objects[user_id] = s
    await ctx.send(content=f"Check your DMs {getName(ctx)}")
    await ctx.author.send(f'Authenticate Spotify here: {s.getAuthUrl()}. Follow sign-on instructions and once provided the key, execute: $$connectSpotify <key>')



# @bot.command(name='connectSpotify', help='Connects to spotify')
@slash.slash(
    name='connect_spotify',
    description='Connects to spotify with key from authSpotify link',
    options=[
        {
            'name': 'key',
            'description': 'Given user key for authentication',
            'type': SlashCommandOptionType.STRING,
            'required': True
        }
    ],
    guild_ids=guild_ids
)
async def connectSpotify(ctx, key):
    await ctx.defer()
    print(f"author: {ctx.author}\nid: {ctx.author_id}")
    user_id = str(ctx.author_id)
    if user_id not in spotify_objects:
        await ctx.send(content='Error: First, you need to sign in and get a specialized access key by using "authSpotify" command')
        return
    # try:
    url_with_token = requests.get(f"{SPOTIPY_REDIRECT_URI}token?key={key}").text
    # except:
    #     print("connectSpotify: Key Error")
    s = spotify_objects[user_id]   # not checking if token needs refresh
    spotify_name = s.authenticate(url_with_token)
    await ctx.send(content=f"Welcome {spotify_name}! Your spotify has been connected!")



async def getSpotifyObj(ctx: SlashContext):
    user_id = str(ctx.author_id)
    if user_id not in spotify_objects:
        await ctx.send(content='Error: You need to sign into your spotify first with "authSpotify" then "connectSpotify <key>"')
        return None
    else:
        return spotify_objects[user_id]



# @bot.command(name='spotify', help='Connects to spotify')
# async def spotifyCommands(ctx, command, **args):
#     user_id = ctx.message.author.id
#     if user_id not in spotify_objects:
#         await ctx.send('Error: You need to sign into your spotify first with "authSpotify" then "connectSpotify <key>"')
#         return
#     s = spotify_objects[user_id]
#     if command.lower() == "now":
#         await playNow(ctx, s)
#     else:
#         await ctx.send('Spotify command not implemented')
#     # TODO: check if token is still good
    

@slash.slash(
    name='spotify_now',
    description='Adds the current song playing in spotify to queue',
    guild_ids=guild_ids
)
async def spotifyNow(ctx: SlashContext):
    await ctx.defer()
    s = await getSpotifyObj(ctx)
    if s is None:  # spotify not authenticated yet
        return
    auth_url = s.getAuthUrl()
    name = s.authenticate(auth_url)
    cs = s.sp.currently_playing()   # "current song"
    if cs is None or cs['is_playing'] is False:
        await ctx.send(content='Nothing is currently playing SILLY.')
        return
    
    album = cs['item']['album']['name']
    artist = cs['item']['artists'][0]['name']
    song_name = cs['item']['name']
    query = f"{song_name} by {artist} on {album}"
    await _play(ctx, query=query)


@slash.slash(
    name='spotify_next',
    description='Adds the next <n> songs in spotify queue to discord queue',
    options=[
        {
            'name': 'n',
            'description': '# of songs to add',
            'type': SlashCommandOptionType.INTEGER,
            'required': True
        }
    ],
    guild_ids=guild_ids
)
async def spotifyNext(ctx: SlashContext, n):
    await ctx.defer()
    s = await getSpotifyObj(ctx)
    if s is None:  # spotify not authenticated yet
        return
    # ^ repeat code
    m_queries = []
    pause = False
    for i in range(n):
        cs = s.sp.currently_playing()   # "current song"
        if not cs:
            await ctx.send(content='Start playing something on Spotify')
            return
        if i==0 and not cs['is_playing']:
            pause = True
        album = cs['item']['album']['name']
        artist = cs['item']['artists'][0]['name']
        song_name = cs['item']['name']
        query = f"{song_name} by {artist} on {album}"
        m_queries.append(query)
        if i != n - 1:
            try:
                sp.next_track() # skip to next song
            except:
                break
    for i in range(n - 1):
        try:
            sp.previous_track() # go to previous song
        except:
            break
    if len(m_queries) == 0:
        await ctx.send(content='Unable to fetch any songs from Spotify')
        return
    await _play(ctx, query=m_queries[0], m_queries=m_queries)



# if __name__=="__main__":
#     client.run(os.environ.get("DISCORD_TOKEN"))

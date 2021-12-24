import discord
from secrets import discord_key

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    
    elif message.content.startswith('$$'):
        await message.channel.send('Sean is a cuck')

client.run(discord_key)
from api import app
from bot import client
# import threading
# import asyncio

# loop = asyncio.get_event_loop()

# async def bootup_bot():
#     client.run(DISCORD_TOKEN)



if __name__=="__main__":
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    if DISCORD_TOKEN is None:
        raise Exception("No discord token provided")
    client.run(DISCORD_TOKEN)

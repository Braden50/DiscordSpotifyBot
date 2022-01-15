from bot import client
import os
import threading


threads = []

if __name__=="__main__":
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    if DISCORD_TOKEN is None:
        raise Exception("No discord token provided")
    client.run(DISCORD_TOKEN)



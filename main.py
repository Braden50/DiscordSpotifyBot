from api import app
from bot import client
import os
import threading
# import threading
# import asyncio

# loop = asyncio.get_event_loop()

# async def bootup_bot():
#     client.run(DISCORD_TOKEN)

threads = []

if __name__=="__main__":
    print("HELLO")
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    if DISCORD_TOKEN is None:
        raise Exception("No discord token provided")
    x = threading.Thread(target=client.run, args=(DISCORD_TOKEN,))
    threads.append(x)
    x.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    print("APP SHOULD BE RUNNING")



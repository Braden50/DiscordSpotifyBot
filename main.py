from api import app, DISCORD_TOKEN
from bot import client
import threading
import asyncio

loop = asyncio.get_event_loop()

async def bootup_bot():
    client.run(DISCORD_TOKEN)

if __name__=="__main__":
    loop.run_until_complete(bootup_bot())
    app.run(debug=False, use_reloader=False)
    
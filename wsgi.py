from api import app, DISCORD_TOKEN
from bot import client


if __name__ == "__main__":
    # x = threading.Thread(target=app.run)
    # x.start()
    # y = threading.Thread(target=client.run, args=(DISCORD_TOKEN,))
    # y.start()
    client.run(DISCORD_TOKEN)
    # app.run()



# sudo apt install uwsgi-core
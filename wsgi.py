from api import app, DISCORD_TOKEN
from bot import client


if __name__ == "__main__":
    x = threading.Thread(target=app.run)
    x.start()
    client.run(DISCORD_TOKEN)
    # app.run(debug=True)



# sudo apt install uwsgi-core
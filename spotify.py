import appSecrets
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from spotipy.oauth2 import SpotifyClientCredentials

website_url = 'https://braden-discord-bot.herokuapp.com/'
os.environ['SPOTIPY_CLIENT_ID'] = appSecrets.SPOTIFY_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = appSecrets.SPOTIFY_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://example.com/callback/'


username = '3bgUrO2zRjKTSVQtuxAndA'

scopes = [
    'ugc-image-upload',
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'user-read-private',
    'user-read-email',
    'user-follow-modify',
    'user-follow-read',
    'user-library-modify',
    'user-library-read',
    'streaming',
    'app-remote-control',
    'user-read-playback-position',
    'user-top-read',
    'user-read-recently-played',
    'playlist-modify-private',
    'playlist-read-collaborative',
    'playlist-read-private',
    'playlist-modify-public'
]

scope_str = " ".join(scopes)
print(scope_str)


class Spotify:
    def __init__(self):
        self.token = None
        self.sp = None
    
    def initialize(self):
        auth_manager = SpotifyClientCredentials()
        try:
            self.token = spotipy.util.prompt_for_user_token(scope=scope_str, show_dialog=False)
        except:
            os.remove(f".cache-{username}")
            self.token = spotipy.util.prompt_for_user_token(scope=scope_str, show_dialog=False)
        self.sp = spotipy.Spotify(auth=self.token, auth_manager=auth_manager)
    
    def printUser(self):
        print("HERE")
        user = self.sp.current_user()
        displayName = user['display_name']
        followers = user['followers']['total']
        print(displayName, followers)

if __name__=="__main__":
    sp = Spotify()
    sp.initialize()
    sp.printUser()



# Erase cache and prompt user permission
# try:

# token = spotipy.util.prompt_for_user_token(scope=scope_str)

# except:
#     os.remove(f".cache-{username}")
#     token = util.prompt_for_user_token(username)

# spotifyObject = spotipy.Spotify(auth=token)

# auth_manager = SpotifyClientCredentials()
# sp = spotipy.Spotify(auth=token, auth_manager=auth_manager)




# --------------------------------
# print("HERE")
# user = sp.current_user()
# print(user)
# displayName = user['display_name']
# followers = user['followers']['total']

# playlists = sp.user_playlists('spotify')
# print(sp.current_user())
# while playlists:
#     for i, playlist in enumerate(playlists['items']):
#         print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
#     if playlists['next']:
#         playlists = sp.next(playlists)
#     else:
#         playlists = None
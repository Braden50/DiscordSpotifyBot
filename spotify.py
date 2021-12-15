# import appSecrets
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from spotipy.oauth2 import SpotifyClientCredentials
import requests
# from appSecrets import website_url
import sys, time


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


class Spotify:
    def __init__(self):
        self.token = None
        self.auth_manager = SpotifyOAuth(scope=scope_str)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        

    def getAuthUrl(self):
        return self.auth_manager.get_authorize_url()
    
    def authenticate(self, url, local=False):
        # print(url)
        if local:
            pass # TODO
        else:
            code = self.auth_manager.parse_response_code(url)
            token = self.auth_manager.get_access_token(code)
            self.sp.auth = token
        user = self.sp.current_user()
        displayName = user['display_name']
        return displayName
        # spotipy.Spotify(auth=self.token, auth_manager=auth_manager)
            
          

        # "    spotipy.Spotify(auth_manager=auth_manager)
        # self.token = spotipy.util.prompt_for_user_token(scope=scope_str, show_dialog=False)
        # except:
        #     os.remove(f".cache-{username}")
        #     self.token = spotipy.util.prompt_for_user_token(scope=scope_str, show_dialog=False)
        # self.sp = spotipy.Spotify(auth=self.token, auth_manager=auth_manager)
        #
        # 
        # 
        #  self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def printUser(self):
        print(1, "HERE")
        user = self.sp.current_user()
        print(2, "HERE")
        displayName = user['display_name']
        followers = user['followers']['total']
        print(displayName, followers)

if __name__=="__main__":
    s = Spotify()
    auth_url = s.getAuthUrl()
    name = s.authenticate(auth_url)
    cs = s.sp.currently_playing()
    if cs is None:
        exit() # nothing playing rn
    print(s.sp.currently_playing())
    
    album = cs['item']['album']['name']
    artist = cs['item']['artists'][0]['name']
    song_name = cs['item']['name']
    is_playing = cs['is_playing']
    print(f"{song_name} by {artist} on {album}. Is playing? {is_playing}")

    
    # s.printUser()



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
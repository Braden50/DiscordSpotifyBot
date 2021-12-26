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
    # testing below
    s = Spotify()
    auth_url = s.getAuthUrl()
    n = 3
    m_queries = []
    attempts = 4
    temp_song_name = ""
    num_previous = n
    pause = False
    new = True
    try:
        initial_volume = s.sp.current_playback()['device']['volume_percent']
    except:
        initial_volume = 0
    s.sp.volume(0)   # mute spotify so skipping isn't heard
    for i in range(n):
        for _ in range(attempts):
            cs = s.sp.currently_playing()   # "current song"
            if not cs:
                print('No current song playing')
            if i == 0 and not cs['is_playing']:
                pause = True
            
            album = cs['item']['album']['name']
            artist = cs['item']['artists'][0]['name']
            song_name = cs['item']['name']

            if temp_song_name != song_name:
                temp_song_name = song_name
                new = True
                break
            else:  # need to wait for skip to go through
                print(temp_song_name, song_name, "waiting")
                time.sleep(1)
                new = False
        # Unable to yield new song
        if not new:
            num_previous = i
            break
        query = f"{song_name} by {artist} on {album}"
        m_queries.append(query)
        s.sp.next_track() # skip to next song
    for _ in range(num_previous):
        s.sp.previous_track() # go to previous song
    if pause:
        s.sp.pause_playback()  # return to not playing
    s.sp.volume(initial_volume)
    print(m_queries)






    # name = s.authenticate(auth_url)
    # cs = s.sp.currently_playing()
    # if cs is None:
    #     exit() # nothing playing rn
    # print(s.sp.currently_playing())
    # try:
    #     album = cs['item']['album']['name']
    #     artist = cs['item']['artists'][0]['name']
    #     song_name = cs['item']['name']
    #     is_playing = cs['is_playing']
    #     print(f"{song_name} by {artist} on {album}. Is playing? {is_playing}")

    
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
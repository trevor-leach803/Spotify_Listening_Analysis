from dash import Dash, html
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os


def render(app):
    # This function collects the top 50 tracks for a user using data from the past 6 months after being given permission to access data
    scope = "user-top-read"
    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope, show_dialog=True))

    # Collect the music tracks
    results = sp.current_user_top_tracks(limit=50,time_range='medium_term') 

    # Collect username and ID and add them to results for use later
    user = sp.current_user()
    username = results['username'] = user['display_name'] 
    user_id = results['user_id'] = user['id']

    if data_delete:
        delete_data()

    # Require the user to re-grant permission each time a query is run
    os.remove(r'.cache')

    return(results)
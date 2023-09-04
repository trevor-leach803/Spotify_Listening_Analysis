import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
import shutil
import sys


class Data:
    def __init__(self,connection,cursor):
        self.connection = connection
        self.cursor = cursor
        self.username = ''
        self.user_id = ''
        self.data_delete = False

        try:
            connection.execute("""CREATE TABLE IF NOT EXISTS SONG_INFO(
                song_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT,
                song_title TEXT NOT NULL,
                artist TEXT NOT NULL,
                artist_id TEXT NOT NULL,
                album_title TEXT NOT NULL,
                album_id TEXT NOT NULL,
                release_date TEXT NOT NULL,
                duration INT NOT NULL,
                explicit INT NOT NULL,
                song_popularity INT NOT NULL,
                album_image_url TEXT NOT NULL,
                UNIQUE(song_id,user_id));
            """)

            connection.execute("""CREATE TABLE IF NOT EXISTS AUDIO_FEATURES(
                song_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                acousticness REAL NOT NULL,
                danceability REAL NOT NULL,
                energy REAL NOT NULL,
                instrumentalness REAL NOT NULL,
                loudness REAL NOT NULL,
                tempo REAL NOT NULL,
                valence REAL NOT NULL,
                UNIQUE(song_id,user_id));
            """)

            connection.execute("""CREATE TABLE IF NOT EXISTS ARTISTS(
                artist_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                followers INT NOT NULL,
                genres TEXT,
                popularity INT NOT NULL,
                top_track_num INT NOT NULL,
                UNIQUE(artist_id,user_id));
            """)

            connection.execute("""CREATE TABLE IF NOT EXISTS QUERIES(
                user_id TEXT PRIMARY KEY NOT NULL,
                username TEXT);
            """)

        except sqlite3.Error as error:
            print("Error occured: {}".format(error))

    def delete_data(self):
        # Function to delete entries in the table if the user wants to re-query the same library
        self.cursor.execute(f'''DELETE FROM SONG_INFO WHERE USER_ID = "{self.user_id}"''')
        self.cursor.execute(f'''DELETE FROM AUDIO_FEATURES WHERE USER_ID = "{self.user_id}"''')
        self.cursor.execute(f'''DELETE FROM ARTISTS WHERE USER_ID = "{self.user_id}"''')
        self.cursor.execute(f'''DELETE FROM QUERIES WHERE USER_ID = "{self.user_id}"''')

        self.connection.commit()

        # Delete the folder of album covers for the user_id if it exists
        folder_name = 'album_covers/' + self.user_id
        # Check if the folder exists
        if os.path.exists(folder_name) and os.path.isdir(folder_name):
            try:
                shutil.rmtree(folder_name)
                print(f"The folder '{folder_name}' and its contents have been deleted.")
            except OSError as e:
                print(f"Error: {e}")


    def check_database(self):
        # Function to check whether the user being queried is already in the database
        try:
            self.cursor.execute(f'''SELECT * FROM QUERIES WHERE user_id = "{self.user_id}"''')
            user_input = ''
            while user_input.upper() not in ['YES', 'Y', 'NO', 'N']:
                user_input = input("Data for this user is already in the database. Do you want to replace the data and continue with the new query? Y/N ")

            if user_input.upper() == "N" or user_input.upper() == "NO":
                return self.data_delete
            else:
                self.data_delete = True
                return self.data_delete
        except:
            pass

    def collect_songs(self):
        # This function collects the top 50 tracks for a user using data from the past 6 months after being given permission to access data
        scope = "user-top-read"
        sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope, show_dialog=True))

        # Collect the music tracks
        print("Collecting top tracks...")
        results = sp.current_user_top_tracks(limit=50,time_range='medium_term') 

        # Collect username and ID and add them to results for use later
        user = sp.current_user()
        self.username = results['username'] = user['display_name'] 
        self.user_id = results['user_id'] = user['id']

        if self.data_delete:
            self.delete_data()

        # Require the user to re-grant permission each time a query is run
        os.remove(r'.cache')

        return(results)
    
    def add_user(self):
        # This function will add the user to the list of queried users
        print("Adding queried user information to database...")
        self.cursor.execute('''SELECT COUNT(*) FROM QUERIES''')
        if not self.username:
            self.username = self.user_id
        self.cursor.execute(f'''INSERT INTO QUERIES VALUES ('{self.user_id}','{self.username}')''')

    def format_quotes(self,word):
        # This function replaces single single and double quotes in a string to double single or double quotes so they can be saved in the database
        formatted_word = word
        if "'" in word:
            formatted_word = word.replace("'", "''")
        if '"' in word:
            formatted_word = word.replace('"', '""')
        return formatted_word

    def add_top_tracks(self, song_dict):
        # This function adds the top tracks to the table of songs. It also formats the information correctly for saving.
        print("Adding top tracks to database...")

        for index, track in enumerate(song_dict['items']):
            song_id = track['id']
            song_title = self.format_quotes(track['name'])
            artist = self.format_quotes(track['artists'][0]['name'])
            artist_id = track['artists'][0]['id']
            album_title = self.format_quotes(track['album']['name'])
            album_id = track['album']['id']
            release_date = track['album']['release_date']
            duration = track['duration_ms']
            explicit = track['explicit']
            song_popularity = track['popularity']
            album_image_url = track['album']['images'][2]['url']

            self.cursor.execute(f'''INSERT INTO SONG_INFO VALUES ('{song_id}','{self.user_id}','{self.username}','{song_title}','{artist}','{artist_id}','{album_title}','{album_id}','{release_date}','{duration}','{explicit}','{song_popularity}','{album_image_url}')''')
    
    def collect_audio_features(self):
        # This function queries the API for each of the top tracks to obtain important audio features
        client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        print("Adding audio features to database...")

        self.cursor.execute(f'SELECT song_id FROM SONG_INFO WHERE user_id = "{self.user_id}"')
        for id in self.cursor.fetchall():
            features = client.audio_features(id[0])
            self.cursor.execute(f'''INSERT INTO AUDIO_FEATURES VALUES ('{features[0]['id']}','{self.user_id}','{features[0]['acousticness']}','{features[0]['danceability']}','{features[0]['energy']}','{features[0]['instrumentalness']}','{features[0]['loudness']}','{features[0]['tempo']}','{features[0]['valence']}')''')

    def genre_selection(self,genre):
        # This function reads through the list of genres and assigns a standard genre based on the list's contents
        if 'country' in genre:
            return 'Country'
        elif 'r&b' in genre:
            return 'R&B'
        elif 'rap' in genre:
            return 'Rap'
        elif 'hip hop' in genre:
            return 'Hip Hop'
        elif 'edm' in genre:
            return 'EDM'
        elif 'pop' in genre:
            return 'Pop'
        elif 'rock' in genre:
            return 'Rock'
        elif 'metal' in genre:
            return 'Metal'
        else:
            return 'Other'

    def num_of_artist_tracks(self,artist_id):
        # This function returns the number of tracks an artist has in the queried list of top tracks
        self.cursor.execute(f'SELECT top_track_num from ARTISTS WHERE artist_id = "{artist_id}" and user_id = "{self.user_id}"')
        count = 1
        for entry in self.cursor.fetchall():
            count += entry[0]
        return count

    def collect_artist_info(self):
        # This function queries the API for each top track to obtain information on the artist
        client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        print("Adding artist information to database...")

        self.cursor.execute(f'SELECT artist_id FROM SONG_INFO WHERE user_id = "{self.user_id}"')
        for id in self.cursor.fetchall():
            info = client.artist(id[0])
            if len(info['genres']) > 0:
                for entry in info['genres']:  # Find standardized genre
                    genre = self.genre_selection(entry)  
                    if genre != 'Other':
                        break
            else:
                genre = 'N/A'
            count = self.num_of_artist_tracks(info['id'])
            # Add new artist to table if they aren't logged already. Otherwise, update the top_track_num field
            if count == 1:
                self.cursor.execute(f'''INSERT OR IGNORE INTO ARTISTS VALUES ('{info['id']}','{self.user_id}','{info['name']}','{info['followers']['total']}','{genre}','{info['popularity']}',{count})''')
            else:
                self.cursor.execute(f'''UPDATE ARTISTS SET top_track_num = "{count}" WHERE artist_id = "{info['id']}"''')
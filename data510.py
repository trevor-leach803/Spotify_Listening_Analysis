import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
import sqlite3
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# Parse the credentials text file to collect the client ID, client secret ID, and the redirect uri
with open(r'credentials.txt') as credentials:
    creds = []
    lns = credentials.readlines()
    for ln in lns:
        creds.append(ln.split())
    os.environ['SPOTIPY_CLIENT_ID'] = creds[0][1]
    os.environ['SPOTIPY_CLIENT_SECRET'] = creds[1][1]
    os.environ['SPOTIPY_REDIRECT_URI'] = creds[2][1] 


def collect_songs():
    # This function collects the top 50 tracks for a user using data from the past 6 months after being given permission to access data
    scope = "user-top-read"
    sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope, show_dialog=True))

    # Collect the music tracks
    print("Collecting top tracks...")
    results = sp.current_user_top_tracks(limit=50,time_range='medium_term') 
    # Collect username and ID and add them to results for use later
    user = sp.current_user()
    results['username'] = user['display_name'] 
    results['user_id'] = user['id']

    # Require the user to re-grant permission each time a query is run
    os.remove(r'.cache')

    return(results)


def collect_audio_features(cursor, user_id):
    # This function queries the API for each of the top tracks to obtain important audio features
    client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    print("Adding audio features to database...")

    cursor.execute(f'SELECT song_id FROM SONG_INFO WHERE user_id = "{user_id}"')
    for id in cursor.fetchall():
        features = client.audio_features(id[0])
        cursor.execute(f'''INSERT INTO AUDIO_FEATURES VALUES ('{features[0]['id']}','{user_id}','{features[0]['acousticness']}','{features[0]['danceability']}','{features[0]['energy']}','{features[0]['instrumentalness']}','{features[0]['loudness']}','{features[0]['tempo']}','{features[0]['valence']}')''')


def collect_artist_info(cursor, user_id):
    # This function queries the API for each top track to obtain information on the artist
    client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    print("Adding artist information to database...")

    cursor.execute(f'SELECT artist_id FROM SONG_INFO WHERE user_id = "{user_id}"')
    for id in cursor.fetchall():
        info = client.artist(id[0])
        if len(info['genres']) > 0:
            for entry in info['genres']:  # Find standardized genre
                genre = genre_selection(entry)  
                if genre != 'Other':
                    break
        else:
            genre = 'N/A'
        count = num_of_artist_tracks(cursor,info['id'],user_id)
        # Add new artist to table if they aren't logged already. Otherwise, update the top_track_num field
        if count == 1:
            cursor.execute(f'''INSERT OR IGNORE INTO ARTISTS VALUES ('{info['id']}','{user_id}','{info['name']}','{info['followers']['total']}','{genre}','{info['popularity']}',{count})''')
        else:
            cursor.execute(f'''UPDATE ARTISTS SET top_track_num = "{count}" WHERE artist_id = "{info['id']}"''')


def format_quotes(word):
    # This function replaces single single and double quotes in a string to double single or double quotes so they can be saved in the database
    formatted_word = word
    if "'" in word:
        formatted_word = word.replace("'", "''")
    if '"' in word:
        formatted_word = word.replace('"', '""')
    return formatted_word


def num_of_artist_tracks(cursor,artist_id,user_id):
    # This function returns the number of tracks an artist has in the queried list of top tracks
    cursor.execute(f'SELECT top_track_num from ARTISTS WHERE artist_id = "{artist_id}" and user_id = "{user_id}"')
    count = 1
    for entry in cursor.fetchall():
        count += entry[0]
    return count


def genre_selection(genre):
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


def add_user(cursor,user_id,username):
    # This function will add the user to the list of queried users
    print("Adding queried user information to database...")
    cursor.execute('''SELECT COUNT(*) FROM QUERIES''')
    user_num = cursor.fetchone()[0] + 1
    if not username:
        username = user_id
    cursor.execute(f'''INSERT INTO QUERIES VALUES ('{user_id}','{username}','{user_num}')''')


def add_top_tracks(song_dict, cursor, username, user_id):
    # This function adds the top tracks to the table of songs. It also formats the information correctly for saving.
    print("Adding top tracks to database...")

    for index, track in enumerate(song_dict['items']):
        song_id = track['id']
        song_title = format_quotes(track['name'])
        artist = format_quotes(track['artists'][0]['name'])
        artist_id = track['artists'][0]['id']
        album_title = format_quotes(track['album']['name'])
        album_id = track['album']['id']
        release_date = track['album']['release_date']
        duration = track['duration_ms']
        explicit = track['explicit']
        song_popularity = track['popularity']
        album_image_url = track['album']['images'][2]['url']

        cursor.execute(f'''INSERT INTO SONG_INFO VALUES ('{song_id}','{user_id}','{username}','{song_title}','{artist}','{artist_id}','{album_title}','{album_id}','{release_date}','{duration}','{explicit}','{song_popularity}','{album_image_url}')''')


def create_database(connection):
    # This function creates the database tables
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
            username TEXT,
            user_num INT NOT NULL);
        """)

    except sqlite3.Error as error:
        print("Error occured: {}".format(error))


def parallel_coordinates_audio_features(user_id,user,connection):
    # This function generates a parallel coordinate plot for audio features from a user's top tracks
    pc_df = pd.read_sql_query(f'SELECT * from audio_features WHERE user_id = "{user_id}"', connection)
    title = f"Audio Features for {user}'s Top Tracks"
    pc_fig = px.parallel_coordinates(pc_df,dimensions=['instrumentalness','acousticness','loudness','danceability','energy','tempo','valence'],title=title)
    pc_fig.show()


def sunburst_genres(user_id,user,connection):
    # This function generates a sunburst plot for a user's top artists and their popularity
    sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{user_id}"', connection)
    labels = {'top_track_num':'Number of Top Tracks', 'popularity':'Artist Popularity', 'labels':'Artist', 'parent':'Genre'}
    title = f"Genres for {user}'s Top Artists"
    sun_fig = px.sunburst(sun_df, path=['genres','artist_name'],values='top_track_num',color='popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
    sun_fig.show()


def violin_plot_valence(connection):
    # This function generates a violin plot to compare all queried users' valence values
    sns.set(font_scale=1.5)
    violin_df = pd.read_sql_query('SELECT valence,username from AUDIO_FEATURES INNER JOIN QUERIES on AUDIO_FEATURES.user_id = QUERIES.user_id', connection)
    sns.violinplot(x=violin_df['valence'], y=violin_df['username'], notch=True, width=0.5)
    plt.title('Valence in Top Tracks', fontsize=30)
    plt.show()


def getImage(path, zoom=1):
    return OffsetImage(plt.imread(path), zoom=zoom)


def scatterplot(user_id,user,connection):
    # This function generates a scatter plot of artist vs. song popularity and plots the song's album cover
    scatter_df = pd.read_sql_query(f'SELECT song_info.user_id,album_title,song_popularity,popularity,album_image_url from SONG_INFO INNER JOIN ARTISTS on SONG_INFO.artist_id = ARTISTS.artist_id WHERE song_info.user_id = "{user_id}"', connection)

    directory = scatter_df['user_id'][0]
    parent_dir = os.getcwd()
    path = os.path.join(parent_dir, directory)

    x = []
    y = []
    paths = []

    # Create a new directory in the current directory to save the images to
    if not os.path.exists(path):
        os.mkdir(path)

    # Retrieve the image from the URL, save it, and re-save it as a PNG for plotting
    for value in scatter_df.index:
        response = requests.get(scatter_df['album_image_url'][value])
        if response.status_code:
            album_title = scatter_df['album_title'][value]
            if '/' in album_title:
                album_title = scatter_df['album_title'][value].replace('/','')
            jpegfilename = path+'/'+album_title+'.jpeg'
            pngfilename = path+'/'+album_title+'.png'
            with open(jpegfilename, 'wb') as image:
                image.write(response.content)
    
            png = Image.open(jpegfilename)
            png.save(pngfilename)

            # Append the values to the lists for plotting
            x.append(scatter_df['popularity'][value])
            y.append(scatter_df['song_popularity'][value])
            paths.append(pngfilename)

    # Create the plot
    plt.rcParams['figure.figsize'] = (22,20)
    fig, ax = plt.subplots()
    ax.scatter(x, y) 
    ax.set_xlim([0,100])
    ax.set_ylim([0,100])
    plt.title(f'Artist and Song Popularity for {user}\'s Top Tracks', fontsize=30)
    plt.xlabel('Artist Popularity', fontsize=20)
    plt.ylabel('Song Popularity', fontsize=20)

    # Plot the image on the scatter plot
    for x0, y0, path in zip(x, y, paths):
        ab = AnnotationBbox(getImage(path), (x0, y0), frameon=False)
        ax.add_artist(ab)

    plt.show()


def main():
    query = True
    connection = sqlite3.connect('spotify_data.db')
    cursor = connection.cursor()
    create_database(connection)

    while query:
        # Collect the data from the API
        top_tracks = collect_songs()
        username = top_tracks['username']
        user_id = top_tracks['user_id']
        add_user(cursor,user_id,username)
        add_top_tracks(top_tracks,cursor,username,user_id)
        collect_audio_features(cursor,user_id)
        collect_artist_info(cursor,user_id)
        connection.commit()

        if username:
            user = username
        else:
            user = user_id

        # Generate visualizations
        parallel_coordinates_audio_features(user_id,user,connection)
        sunburst_genres(user_id,user,connection)
        scatterplot(user_id,user,connection)

        user_input = ''
        while user_input.upper() not in ['YES', 'Y', 'NO', 'N']:
            user_input = input("Would you like to query another library? Y/N ")
        if user_input.upper() == "N" or user_input.upper() == "NO":
            query = False
            violin_plot_valence(connection)
            connection.close()
            break         


if __name__ == '__main__':
    main()